
import random

class Bot:
    """ A bot class. Override this class to implement your own Connect6 AI. """

    def __init__(self, player=1):
        self.player = player

    def move(self, board, nth_move):
        raise NotImplementedError("Implement this to build your own AI.")
        pass

    @property
    def bot_kind(self):
        return self.__class__.__name__


class RandomBot(Bot):

    """ Example bot that runs randomly. """
    def move(self, board, nth_move):
        x = random.randrange(0, 19)
        y = random.randrange(0, 19)
        input()
        return x, y

