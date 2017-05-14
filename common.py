
from collections import namedtuple

X_TO_CHAR = {i : chr(ord('A') + i) for i in range(19)}
CHAR_TO_X = {chr(ord('A') + i): i for i in range(19)}


def repr_direction(dir_func):
    dx, dy = dir_func(0, 0)  # differentiate
    return '({}, {})'.format(dy, dx)


class Point(namedtuple('Point', ['x', 'y'])):

    @staticmethod
    def from_name(name):
        x = CHAR_TO_X[name.capitalize()[0]]
        y = int(name[1:])-1
        return Point(x, y)

    @property
    def name(self):
        return X_TO_CHAR[self.x] + str(self.y+1)

    # some memory optimization
    __slots__ = ()

    def __str__(self):
        return '{} ({},{})'.format(self.name, self.x, self.y)


class Debugger:
    def __init__(self, enable_log=False):
        self.enable_log = enable_log

    def log(self, str):
        if self.enable_log:
            print(str)


    def stop(self):
        if self.enable_log:
            input('[Press any key to resume]')

