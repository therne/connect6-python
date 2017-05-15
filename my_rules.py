
from common import Point, Debugger, repr_direction
debug = Debugger(enable_log=False)

class StragiticStatus:
    def __init__(self):
        self.a = 0
        self.a_point = []
        self.b = 0
        self.b_point = []

# 8방향
DIRECTIONS = [
    (1, 0),
    (1, 1),
    (1, -1),
    (0, 1),
    (0, -1),
    (-1, 0),
    (-1, 1),
    (-1, -1)
]


def reverse_of(dir):
    dx, dy = dir
    return (-dx, -dy)


def is_outta_range(x, y):
    return x < 0 or x >= 19 or y < 0 or y >= 19


def track(board, start_x, start_y, dir_func):
    pass

def scan_from_last(board, last_points, player):
    for point in last_points:
        x, y = point

        # check 8 directions and start backtracking.
        for dir in DIRECTIONS:
            dx, dy = dir
            nx, ny = x+dx, y+dy
            if is_outta_range(nx, ny): continue

            if board[ny][nx] == board[y][x]:
                debug.log('Direction {}'.format(dir))
                debug.log('Start at {}'.format(Point(x, y)))

                # to check properly, go to the end of direction
                while board[ny][nx] == board[y][x]:
                    nx += dx
                    ny += dy
                    if is_outta_range(nx, ny): break

                dx, dy = reverse_of(dir)

                debug.log('End of direction : {}'.format(Point(nx, ny)))

                is_end = track(board, nx, ny, reverse_of(dir))
                if is_end:
                    # returns player who won.
                    return board[ny][nx]

                debug.stop()

def scan_full(board) -> StragiticStatus:

    pass