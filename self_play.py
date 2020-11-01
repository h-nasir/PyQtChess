from common import starting_fen
from position import Position
from search import Search as SearchA
from search2 import Search as SearchB

search_a_wins = 0
search_b_wins = 0
draws = 0


def play(a_is_white):
    position = Position(starting_fen)
    search_a = SearchA(position)
    search_b = SearchB(position)

    if a_is_white:
        while True:
            # White
            move = search_a.iter_search(time_limit=0.1)
            position = search_a.position
            position.make_move(move)

            if position.is_game_over():
                game_over(position, a_is_white)
                return

            # Black
            move = search_b.iter_search(time_limit=0.1)
            position = search_b.position
            position.make_move(move)

            if position.is_game_over():
                game_over(position, a_is_white)
                return
    else:
        while True:
            # White
            move = search_b.iter_search(time_limit=0.1)
            position = search_b.position
            position.make_move(move)

            if position.is_game_over():
                game_over(position, a_is_white)
                return

            # Black
            move = search_a.iter_search(time_limit=0.1)
            position = search_a.position
            position.make_move(move)

            if position.is_game_over():
                game_over(position, a_is_white)
                return


def game_over(position, a_is_white):
    global search_a_wins
    global search_b_wins
    global draws

    print()
    
    if not list(filter(position.is_legal, position.get_pseudo_legal_moves())):
        # Checkmate
        if position.is_in_check():
            if position.colour:
                print("White wins by checkmate")
                if a_is_white:
                    search_a_wins += 1
                else:
                    search_b_wins += 1
            else:
                print("Black wins by checkmate")
                if a_is_white:
                    search_b_wins += 1
                else:
                    search_a_wins += 1
        # Stalemate
        else:
            print("Draw by stalemate")
            draws += 1
    # Fifty-move rule
    elif position.halfmove_clock >= 100:
        print("Draw by fifty-move rule")
        draws += 1
    # Threefold repetition
    else:
        print("Draw by threefold repetition")
        draws += 1

    total = search_a_wins + search_b_wins + draws
    print("Total games: {}".format(total))
    print("Search A wins: {:.2f}%".format((search_a_wins / total) * 100))
    print("Search B wins: {:.2f}%".format((search_b_wins / total) * 100))
    print("Draws: {:.2f}%".format((draws / total) * 100))
    print()


a_is_white = True
while True:
    play(a_is_white)
    a_is_white = not a_is_white
