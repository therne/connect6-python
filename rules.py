
from common import Point, Debugger, repr_direction
debug = Debugger(enable_log=False)

# 8방향에 대한 함수들
DIRECTIONS = [
    lambda x, y: (x+1, y),
    lambda x, y: (x+1, y+1),
    lambda x, y: (x+1, y-1),
    lambda x, y: (x-1, y),
    lambda x, y: (x-1, y+1),
    lambda x, y: (x-1, y-1),
    lambda x, y: (x, y-1),
    lambda x, y: (x, y+1),
]


def reverse_of(dir_func):
    """ 방향함수에 대한 역방향 함수를 리턴한다. """
    dx, dy = dir_func(0, 0)  # differentiate
    return lambda x, y: (x-dx, y-dy)


def is_outta_range(x, y):
    return x < 0 or x >= 19 or y < 0 or y >= 19


class Referee:
    """ 그 자리에 돌을 놓을 수 있는지, 누가 이겼는지를 판단하는 심판 클래스이다. """

    def __init__(self, initial_board):
        self.board = initial_board
        self.last_move = (0, 0)

    def update(self, x, y, player):
        self.board[y][x] = player
        self.last_move = (x, y)

    def determine(self) -> int:
        """ Determine who won.
        :return: player number who won. None if there's no winner (game isn't finished).
        """
        board = self.board
        x, y = self.last_move

        # check 8 directions and start backtracking.
        for dir_func in DIRECTIONS:
            nx, ny = dir_func(x, y)
            if is_outta_range(nx, ny): continue

            if board[ny][nx] == board[y][x]:
                debug.log('Direction : ' + repr_direction(dir_func))
                debug.log('Start at {}'.format(Point(x, y)))

                # to check properly, go to the end of direction
                while board[ny][nx] == board[y][x]:
                    nx, ny = dir_func(nx, ny)
                    if is_outta_range(nx, ny): break

                reverse_dir_func = reverse_of(dir_func)
                nx, ny = reverse_dir_func(nx, ny)  # one step back.

                debug.log('End of direction : {}'.format(Point(nx, ny)))

                is_end = self._track(nx, ny, reverse_dir_func)
                if is_end:
                    # returns player who won.
                    return board[ny][nx]

                debug.stop()


    def _track(self, start_x, start_y, dir_func):
        x, y = start_x, start_y
        original_player = self.board[y][x]
        debug.log('Track started at {}'.format(Point(x, y)))

        step = 1
        while True:
            x, y = dir_func(x, y)
            if is_outta_range(x, y) or self.board[y][x] != original_player:
                if step == 6: return True
                debug.log('Track finished at step {}'.format(step))
                return False
            step += 1

        if step > 6:
            debug.log('Track success, but too many steps (step={})'.format(step))
            return False

        return True


    def can_place(self, x, y):
        if self.board[y][x] != 0:
            return False, 'Duplicated move'

        return True, 'Ok'
