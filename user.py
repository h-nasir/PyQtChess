import pickle


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.wins = 0
        self.losses = 0
        self.draws = 0

        self.history = [0]

        self.saved_game = None

    def add_win(self):
        self.wins += 1
        total = self.wins + self.losses + self.draws
        win_percent = (self.wins / total) * 100
        self.history.append(win_percent)

    def add_loss(self):
        self.losses += 1
        total = self.wins + self.losses + self.draws
        win_percent = (self.wins / total) * 100
        self.history.append(win_percent)

    def add_draw(self):
        self.draws += 1
        total = self.wins + self.losses + self.draws
        win_percent = (self.wins / total) * 100
        self.history.append(win_percent)


def create_user(username, password):
    try:
        with open('accounts.pkl', 'rb') as accounts_file:
            accounts = pickle.load(accounts_file)
    except FileNotFoundError:
        accounts = {}

    accounts[username] = User(username, password)
    with open('accounts.pkl', 'wb') as accounts_file:
        pickle.dump(accounts, accounts_file)


def get_user(username):
    try:
        with open('accounts.pkl', 'rb') as accounts_file:
            accounts = pickle.load(accounts_file)
    except (FileNotFoundError, KeyError):
        print("No account with the username {}".format(username))
    else:
        return accounts[username]


def update_user(updated_user):
    try:
        with open('accounts.pkl', 'rb') as accounts_file:
            accounts = pickle.load(accounts_file)
            user = accounts[updated_user.username]
    except (FileNotFoundError, KeyError):
        print("No account with the username {}".format(updated_user.username))
    else:
        user.wins = updated_user.wins
        user.losses = updated_user.losses
        user.draws = updated_user.draws
        user.history = updated_user.history
        user.saved_game = updated_user.saved_game

        with open('accounts.pkl', 'wb') as accounts_file:
            pickle.dump(accounts, accounts_file)


def username_available(username):
    try:
        with open('accounts.pkl', 'rb') as accounts_file:
            accounts = pickle.load(accounts_file)
    except (FileNotFoundError, KeyError):
        return True
    else:
        if username in accounts:
            return False
        return True
