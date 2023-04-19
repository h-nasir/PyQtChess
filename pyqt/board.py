import copy

from PyQt5.QtCore import pyqtSignal, QPropertyAnimation, QEventLoop, QRegExp, Qt, QThread
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QFrame, QGridLayout, QLabel, QMessageBox, QSizePolicy, QWidget

import common
from consts import CASTLING, PROMOTION, KNIGHT_PROMOTION, BISHOP_PROMOTION, ROOK_PROMOTION, QUEEN_PROMOTION
from position import Position
from search import Search

SQR_SIZE = 100


class ChessBoard(QFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.user = self.parent.parent.user

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)

        self.layout = QGridLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.draw_squares()
        self.setLayout(self.layout)

        self.position = Position(common.starting_fen)
        self.user_is_white = self.parent.user_is_white
        self.search = Search(self.position)
        self.search_thread = SearchThread(self)
        self.self_play = False
        self.difficulty = None
        self.autosave = None
        self.saved = True

        self.undone_stack = []

        self.sqr_size = SQR_SIZE

    def setInfo(self, info):
        self.info = info

    def resizeEvent(self, event):
        if event.size().width() > event.size().height():
            self.resize(event.size().height(), event.size().height())
            self.sqr_size = int(event.size().height() / 8)
        else:
            self.resize(event.size().width(), event.size().width())
            self.sqr_size = int(event.size().width() / 8)

    def start_game(self):
        if self.self_play or self.position.colour == self.user_is_white:
            self.disable_pieces()
            self.search_thread.start()
        else:
            self.enable_pieces()

    def draw_squares(self):
        for row, rank in enumerate('87654321'):
            for col, file in enumerate('abcdefgh'):
                square = QWidget(self)
                square.setObjectName(file + rank)
                square.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
                if row % 2 == col % 2:
                    square.setStyleSheet('background-color: #F0D9B5')
                else:
                    square.setStyleSheet('background-color: #B58863')
                self.layout.addWidget(square, row, col)

    def place_piece(self, sqr_name, piece):
        col, row = common.square_to_coords[sqr_name]

        piece_label = PieceLabel(self, piece)
        self.layout.addWidget(piece_label, row, col)

    def piece_at_square(self, sqr_index):
        square = self.findChild(QWidget, common.index_to_san[sqr_index])
        square_pos = self.layout.getItemPosition(self.layout.indexOf(square))
        for piece in self.findChildren(QLabel):
            piece_pos = self.layout.getItemPosition(self.layout.indexOf(piece))
            if square_pos == piece_pos:
                return piece

    def set_fen(self, fen):
        self.position = Position(fen)
        self.search = Search(self.position)
        self.refresh_from_state()

    def set_position(self, position):
        self.position = position
        self.search = Search(self.position)
        self.refresh_from_state()

    def clear(self):
        all_pieces = self.findChildren(QLabel)
        for piece in all_pieces:
            piece.setParent(None)  # Delete piece

    def refresh_from_state(self):
        QApplication.processEvents()
        
        self.clear()
        
        for sqr_index in range(64):
            piece = self.position.squares[sqr_index]
            sqr_name = common.squares_san[sqr_index]
            if piece:
                self.place_piece(sqr_name, piece)                

    def reset(self):
        self.set_fen(common.starting_fen)
        self.refresh_from_state()

        self.position.undo_info.clear()
        self.undone_stack.clear()

    def suggest_move(self):
        self.disable_pieces()

        tt_index = self.position.zobrist & 0xFFFF
        tt_entry = self.search.tt[tt_index]
        
        if tt_entry and tt_entry.zobrist == self.position.zobrist and tt_entry.move and self.position.is_pseudo_legal(tt_entry.move):
            move = tt_entry.move
        else:
            move = self.search.iter_search(time_limit=1)
            self.position = self.search.position

        src_index = (move >> 6) & 0x3F
        dst_index = move & 0x3F

        piece = self.piece_at_square(src_index)
        self.piece_glide(piece, dst_index)
        self.piece_glide(piece, src_index)
        
        self.enable_pieces()
        self.refresh_from_state()

    def highlight(self, sq):
        # If square index given, convert to SAN
        if not common.regex_square.match(str(sq)):
            sq = common.index_to_san[sq]

        square = self.findChild(QWidget, sq)

        col, row = common.square_to_coords[sq]

        if row % 2 == col % 2:  # light square
            square.setStyleSheet('background-color: #F7EC74')
        else:  # dark square
            square.setStyleSheet('background-color: #DAC34B')

    def unhighlight(self, sq):
        # If square index given, convert to SAN
        if not common.regex_square.match(str(sq)):
            sq = common.index_to_san[sq]

        square = self.findChild(QWidget, sq)

        col, row = common.square_to_coords[sq]

        if row % 2 == col % 2:  # light square
            square.setStyleSheet('background-color: #F0D9B5')
        else:  # dark square
            square.setStyleSheet('background-color: #B58863')

    def unhighlight_all(self):
        for sqr_index in range(64):
            self.unhighlight(sqr_index)

    def moves_from_square(self, sqr_index):
        moves = self.position.get_pseudo_legal_moves()
        moves = [x for x in moves if (x >> 6) & 0x3F == sqr_index]

        # Filter out illegal moves
        moves = list(filter(self.position.is_legal, moves))

        return moves

    def disable_pieces(self):
        for piece in self.findChildren(QLabel):
            piece.is_enabled = False

    def enable_pieces(self):
        for piece in self.findChildren(QLabel):
            piece.is_enabled = True

    def piece_glide(self, piece, dst_index):
        piece.raise_()
        dst_square = self.findChild(QWidget, common.index_to_san[dst_index])
        self.glide = QPropertyAnimation(piece, b'pos')
        self.glide.setDuration(500)
        self.glide.setEndValue(dst_square.pos())
        self.glide.start()

        # Start local event loop, so program waits until glide is completed
        loop = QEventLoop()
        self.glide.finished.connect(loop.quit)
        loop.exec()

    def do_rook_castle(self, king_dst, is_undo):
        if king_dst == 2:
            rook_src = 0
            rook_dst = 3
        elif king_dst == 6:
            rook_src = 7
            rook_dst = 5
        elif king_dst == 58:
            rook_src = 56
            rook_dst = 59
        elif king_dst == 62:
            rook_src = 63
            rook_dst = 61

        if is_undo:
            rook = self.piece_at_square(rook_dst)
            self.piece_glide(rook, rook_src)
        else:
            rook = self.piece_at_square(rook_src)
            self.piece_glide(rook, rook_dst)

    def move_glide(self, move, is_undo):
        src_index = (move >> 6) & 0x3F
        dst_index = move & 0x3F

        if not is_undo:
            piece = self.piece_at_square(src_index)
        else:
            piece = self.piece_at_square(dst_index)

        self.piece_glide(piece, src_index if is_undo else dst_index)

        if move & (0x3 << 14) == CASTLING:
            self.do_rook_castle(dst_index, is_undo)

    def player_move(self, move):
        self.disable_pieces()
        self.info.button_frame.disable_buttons()

        self.position.make_move(move)
        self.refresh_from_state()

        # After a move has been made, the player can no longer redo moves that were undone previously
        self.undone_stack.clear()

        # If player is black, increment fullmove number after player's turn
        if not self.user_is_white:
            self.position.fullmove_number += 1

        self.info.move_frame.update_moves()

        if self.position.is_game_over():
            self.game_over()
        else:
            self.saved = False
            self.search_thread.start()  # Start search thread for computer's move

    def computer_move(self, move):
        self.move_glide(move, False)

        self.position.make_move(move)
        self.refresh_from_state()

        # If computer is black, increment fullmove number after computer's turn
        if self.user_is_white:
            self.position.fullmove_number += 1

        self.info.move_frame.update_moves()

        if self.position.is_game_over():
            self.game_over()
        else:
            if self.autosave:
                self.save()
            else:
                self.saved = False

            if self.self_play:
                self.search_thread.start()
            else:
                self.enable_pieces()

        self.info.button_frame.enable_buttons()

    def game_over(self):
        user = self.parent.parent.user

        legal_moves = list(filter(self.position.is_legal,
                                  self.position.get_pseudo_legal_moves()))

        if not legal_moves:
            # Checkmate
            if self.position.is_in_check():
                text = "{} wins by checkmate".format("White" if self.position.colour else "Black")
                if user:
                    user.add_win() if self.user_is_white == bool(self.position.colour) else user.add_loss()
            # Stalemate
            else:
                text = "Draw by stalemate"
                if user:
                    user.add_draw()
        # Fifty-move rule
        elif self.position.halfmove_clock >= 100:
            text = "Draw by fifty-move rule"
            if user:
                user.add_draw()
        # Threefold repetition
        elif self.position.is_threefold_repetition():
            text = "Draw by threefold repetition"
            if user:
                user.add_draw()
        elif self.position.is_insufficient_material():
            text = "Draw by insufficient material"
            if user:
                user.add_draw()

        msg_box = QMessageBox()
        msg_box.setWindowIcon(QIcon('./assets/icons/pawn_icon.png'))
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Chess")
        msg_box.setText(text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

        self.saved = True

    def save(self):
        self.parent.parent.user.saved_game = copy.deepcopy(self.position)
        self.saved = True


# Search algorithm must be run in a separate thread to the main event loop, to prevent the GUI from freezing
class SearchThread(QThread):
    move_signal = pyqtSignal(int)

    def __init__(self, board):
        super().__init__()

        self.board = board
        self.move_signal.connect(self.board.computer_move)

    def run(self):
        self.board.disable_pieces()

        if self.board.difficulty == 1:
            move = self.board.search.iter_search(max_depth=1)  # Depth 1 search
        elif self.board.difficulty == 2:
            move = self.board.search.iter_search(max_depth=2)  # Depth 2 search
        elif self.board.difficulty == 3:
            move = self.board.search.iter_search(time_limit=0.1)  # 0.1 second search
        elif self.board.difficulty == 4:
            move = self.board.search.iter_search(time_limit=1)  # 1 second search
        elif self.board.difficulty == 5:
            move = self.board.search.iter_search(time_limit=5)  # 5 second search

        self.board.position = self.board.search.position

        self.move_signal.emit(move)


class PieceLabel(QLabel):
    def __init__(self, parent, piece):
        super().__init__(parent)

        self.piece = piece

        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        # Make label transparent, so square behind piece is visible
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.board = parent
        self.is_white = False if self.piece >> 3 else True
        self.is_enabled = True

        self.src_pos = None
        self.mouse_pos = None
        self.src_square = None
        self.dst_square = None
        self.legal_moves = None
        self.legal_dst_squares = None

        # Store original piece image
        pixmap = QPixmap('./assets/pieces/{}{}.png'.format('w' if self.is_white else 'b',
                                                           common.piece_int_to_string[self.piece].lower()))
        self.setPixmap(pixmap)

        # When label is scaled, also scale image inside the label
        self.setScaledContents(True)

        self.setMouseTracking(True)

        self.show()

    def resizeEvent(self, event):
        if event.size().width() > event.size().height():
            self.resize(event.size().height(), event.size().height())
        else:
            self.resize(event.size().width(), event.size().width())

    def enterEvent(self, event):
        if self.is_enabled:
            if self.board.user_is_white == self.is_white:
                # Set open hand cursor while hovering over a piece
                QApplication.setOverrideCursor(Qt.OpenHandCursor)

    def leaveEvent(self, event):
        # Set arrow cursor while not hovering over a piece
        QApplication.setOverrideCursor(Qt.ArrowCursor)

    def mousePressEvent(self, event):
        if self.is_enabled:
            if event.buttons() == Qt.LeftButton:
                if self.board.user_is_white == self.is_white:
                    # Set closed hand cursor while dragging a piece
                    QApplication.setOverrideCursor(Qt.ClosedHandCursor)

                    # Raise piece to the front
                    self.raise_()

                    # Store mouse position and square position, relative to the chessboard
                    self.mouse_pos = self.mapToParent(self.mapFromGlobal(event.globalPos()))
                    self.src_pos = self.mapToParent(self.rect().topLeft())

                    # Snap to cursor
                    offset = self.rect().topLeft() - self.rect().center()
                    self.move(self.mouse_pos + offset)

                    # Identify origin square
                    all_squares = self.board.findChildren(QWidget, QRegExp(r'[a-h][1-8]'))
                    for square in all_squares:
                        if square.pos() == self.src_pos:
                            self.src_square = square
                            break

                    # Identify legal moves
                    sqr_index = common.san_to_index[self.src_square.objectName()]
                    self.legal_moves = self.board.moves_from_square(sqr_index)

                    # Only need destination square for each move
                    self.legal_dst_squares = list(map(lambda move: common.index_to_san[move & 0x3F], self.legal_moves))

                    # Highlight origin and destination squares
                    self.board.highlight(sqr_index)
                    for dst_square in self.legal_dst_squares:
                        self.board.highlight(dst_square)

    def mouseMoveEvent(self, event):
        if self.is_enabled:
            if event.buttons() == Qt.LeftButton:
                if self.board.user_is_white == self.is_white:
                    # Update mouse position, relative to the chess board
                    self.mouse_pos = self.mapToParent(self.mapFromGlobal(event.globalPos()))

                    # Calculate offset from centre to top-left of square
                    offset = self.rect().topLeft() - self.rect().center()

                    # Calculate new x position, not allowing the piece to go outside the board
                    if self.mouse_pos.x() < self.board.rect().left():
                        new_pos_x = self.board.rect().left() + offset.x()
                    elif self.mouse_pos.x() > self.board.rect().right():
                        new_pos_x = self.board.rect().right() + offset.x()
                    else:
                        new_pos_x = self.mouse_pos.x() + offset.x()

                    # Calculate new y position, not allowing the piece to go outside the board
                    if self.mouse_pos.y() < self.board.rect().top():
                        new_pos_y = self.board.rect().top() + offset.y()
                    elif self.mouse_pos.y() > self.board.rect().bottom():
                        new_pos_y = self.board.rect().right() + offset.y()
                    else:
                        new_pos_y = self.mouse_pos.y() + offset.y()

                    # Move piece to new position
                    self.move(new_pos_x, new_pos_y)

    def mouseReleaseEvent(self, event):
        if self.is_enabled:
            if self.board.user_is_white == self.is_white:
                # Set open hand cursor when piece is released
                QApplication.setOverrideCursor(Qt.OpenHandCursor)

                self.board.unhighlight_all()

                # If mouse not released on board, move piece back to origin square, and return
                if not self.board.rect().contains(self.board.mapFromGlobal(event.globalPos())):
                    self.move(self.src_pos)
                    return

                # Identify destination square
                all_squares = self.board.findChildren(QWidget, QRegExp(r'[a-h][1-8]'))
                for square in all_squares:
                    if square.rect().contains(square.mapFromGlobal(event.globalPos())):
                        self.dst_square = square
                        break

                if self.dst_square.objectName() in self.legal_dst_squares:  # If legal move
                    # Snap to destination square
                    self.board.layout.removeWidget(self)
                    row = int(self.dst_square.y() / self.board.sqr_size)
                    col = int(self.dst_square.x() / self.board.sqr_size)
                    self.board.layout.addWidget(self, row, col)

                    src_sqr_index = common.san_to_index[self.src_square.objectName()]
                    dst_sqr_index = common.san_to_index[self.dst_square.objectName()]
                    from_to = (src_sqr_index << 6) + dst_sqr_index

                    # If enemy piece is at destination square, remove it from the board (capture)
                    piece_label = self.board.piece_at_square(dst_sqr_index)
                    if piece_label:
                        if piece_label.is_white != self.is_white:
                            piece_label.setParent(None)

                    for move in self.legal_moves:
                        if move & 0xFFF == from_to:
                            move_made = move

                    move_type = move_made & (0x3 << 14)

                    if move_type == PROMOTION:
                        promotion_prompt = QMessageBox()
                        promotion_prompt.setWindowIcon(QIcon('./assets/icons/pawn_icon.png'))
                        promotion_prompt.setIcon(QMessageBox.Question)
                        promotion_prompt.setWindowTitle("Chess")
                        promotion_prompt.setText("Choose promotion piece.")
                        knight_btn = promotion_prompt.addButton("Knight", QMessageBox.AcceptRole)
                        bishop_btn = promotion_prompt.addButton("Bishop", QMessageBox.AcceptRole)
                        rook_btn = promotion_prompt.addButton("Rook", QMessageBox.AcceptRole)
                        queen_btn = promotion_prompt.addButton("Queen", QMessageBox.AcceptRole)
                        promotion_prompt.exec()

                        if promotion_prompt.clickedButton() == knight_btn:
                            move_made = PROMOTION + KNIGHT_PROMOTION + from_to
                            self.setPixmap(QPixmap('./assets/pieces/{}.png'.format('wn' if self.is_white else 'bn')))
                        elif promotion_prompt.clickedButton() == bishop_btn:
                            move_made = PROMOTION + BISHOP_PROMOTION + from_to
                            self.setPixmap(QPixmap('./assets/pieces/{}.png'.format('wb' if self.is_white else 'bb')))
                        elif promotion_prompt.clickedButton() == rook_btn:
                            move_made = PROMOTION + ROOK_PROMOTION + from_to
                            self.setPixmap(QPixmap('./assets/pieces/{}.png'.format('wr' if self.is_white else 'br')))
                        elif promotion_prompt.clickedButton() == queen_btn:
                            move_made = PROMOTION + QUEEN_PROMOTION + from_to
                            self.setPixmap(QPixmap('./assets/pieces/{}.png'.format('wq' if self.is_white else 'bq')))
                    elif move_type == CASTLING:
                        self.board.do_rook_castle(move_made & 0x3F, False)

                    self.board.player_move(move_made)
                else:
                    # Snap back to origin square
                    self.move(self.src_pos)
