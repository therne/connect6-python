
from common import Point
import os

class Move:
    def __init__(self, x, y, player):
        self.x = x
        self.y = y
        self.player = player

    def __repr__(self):
        name = 'White' if self.player == 1 else 'Black'
        coord = Point(self.x, self.y)
        return '("Move",{},{},{}) # {} at {}'.format(self.player, self.x, self.y, name, coord)


class MoveLogger:

    def __init__(self, logdir='logs/'):
        self.moves = []

        self.logdir = logdir
        if not os.path.exists(self.logdir):
            os.makedirs(logdir)

        self.session_name = self._get_session_name()

    def _get_session_name(self):
        session_name = 1
        try:
            with open(self.logdir + 'session', 'r') as file:
                session_name = int(file.read())
                session_name += 1  # new session.
        except: pass

        self._save_session_name(session_name)
        return session_name

    def _save_session_name(self, session_name):
        with open(self.logdir + 'session', 'w') as file:
            file.write(str(session_name))

    def log(self, x, y, player):
        move = Move(x, y, player)
        self.moves.append(move)

    def undo(self):
        self.moves.pop(len(self.moves)-1)

    def log_winner(self, player):
        name = 'White' if player == 1 else 'Black'
        self.moves.append('("Res", {}) # {} won'.format(player, name))

    def save_to_file(self):
        with open('logs/log.{}.txt'.format(self.session_name), 'w') as file:
            file.writelines('{}\n'.format(move) for move in self.moves)
