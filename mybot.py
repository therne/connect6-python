# 여기서부터 소스가 심각하게 더러워짐.

from bot import Bot
from common import Point, Debugger
from rules import Referee
from my_rules import scan_from_last, scan_full
import math
import time
import random

dbg = Debugger(enable_log=True)

def convert_stone_like_samsung(stone, me):
    if stone == me: return 1
    elif stone == 0: return 0
    elif stone == 3: return 3
    return 2

class MySmartBot(Bot):

    def __init__(self, player=1):
        super(MySmartBot, self).__init__(player=1)
        self.samsung_moves = []
        self.samsung_index = 0


    def move(self, board, nth_move):
        if self.samsung_index == 0:
            s_board = self.convert_board_like_samsung(board)
            self.samsung_moves = samsung_like_move(s_board, nth_move)

        # 왜 samsung-like-move냐? 대회 C++파일은 한번에 두개씩두는데 이건 하나씩임. 그래서 저장해야댐
        ret = self.samsung_moves[self.samsung_index*2:(self.samsung_index+1)*2]

        self.samsung_index += 1
        if self.samsung_index == 2 or nth_move == 1:
            self.samsung_index = 0

        return ret

    def convert_board_like_samsung(self, board):
        me = self.player
        return [[convert_stone_like_samsung(board[y][x], me) for x in range(19)] for y in range(19)]

#============================
# C++ Binding? for faster porting
#=============================
def memcpy(board, size):
    return [[board[y][x] for x in range(19)] for y in range(19)]

def strlen(str):
    return len(str)

def list_unique(items):
    from collections import OrderedDict
    return list(OrderedDict.fromkeys(items))

def chrono_now():
    return int(round(time.time() * 1000))


#============================================================
# Real algorithm part
#============================================================

SEARCH_SPACE_DIRECTIONS = [  # int{}{}
    (-2, -2), (0, -2), (2, -2),
    (-1, -1), (0, -1), (1, -1),
    (-2, 0), (-1, 0), (1, 0), (2, 0),
    (-1, 1), (0, 1), (1, 1),
    (-2, 2), (0, 2), (2, 2)
]

SIMULATE_TIMES = 100
MAX_PLAYOUT_DEPTH = 20
MAX_ROLLOUT_DEPTH = 100
C = 5    # C = UCB parameter
TIMEOUT = 5000/2  # 5 second timeout. 2번돌려야되니까 나누기 2
LAMBDA = 0.4  # 시뮬레이션 승률의 비중.
BOARD_SIZE = 19*19*4 # 4 = sizeof(int)

class Node:

    def __init__(self, parent, policy_prob: float):
        # prior_p: Policy가 결정한 값
        self.parent = parent
        self.children = {}
        self.num_visits = 0
        self.q = 0
        self.policy_prob = policy_prob
        self.u = policy_prob

    def backpropagate(self, leaf_value):
        if self.parent:
            self.parent.backpropagate(leaf_value)

        self._update(leaf_value)

    def select(self):
        # Greedy : 밸류 최고값을 가진놈 선택
        max_value = -100
        max_child = None
        max_move = None
        for move, child in self.children.items():
            value = child.getvalue()
            if max_value < value:
                max_value = value
                max_child = child
                max_move = move

        return max_move, max_child


    def expand(self, policies):
        for move, prob in policies:
            if move not in self.children:
                self.children[move] = Node(parent=self, policy_prob=prob)

    def _update(self, leaf_value):
        self.num_visits += 1
        self.q += (leaf_value - self.q) / self.num_visits  # update Q. (q = Action-value (Average reward(value) of all visits).)
        if self.parent:
            # update u. (u = UCB value)
            self.u = self.policy_prob * C * math.sqrt(self.parent.num_visits) / (1 + self.num_visits)

    def getvalue(self):
        return self.q + self.u

    def is_leaf(self):
        return self.children == {}


win_count = 0
fail_count = 0
draw_count = 0

class MCTS:
    def __init__(self):
        self.root = Node(None, 1.0)

    def move(self, state) -> Point:
        t = 0
        playout_count = 0
        last_time = chrono_now()

        # 시간이 끝날때까지 playout 진행
        while t < TIMEOUT:
            copy_state = state.copy()
            self.playout(copy_state)

            t += chrono_now() - last_time
            last_time = chrono_now()
            del copy_state

            playout_count += 1

        dbg.log('Playout count : {}'.format(playout_count))

        # 가장 많이 방문된 (= 값이 높은)노드를 선택함.
        max_visit = -100
        max_child = None
        max_move = None
        for move, child in self.root.children.items():
            if max_visit < child.num_visits:
                max_visit = child.num_visits
                max_child = child
                max_move = move

        dbg.log('Max visited : {}'.format(max_visit))

        # Root node를 업데이트함. 그 형제들은 전부 없애버림.
        # TODO: 형제의 자식들은?ㅜㅜ
        for _, child in self.root.children.items():
            if child != max_child:
                del child
        # TODO: del self.root
        self.root = max_child
        self.root.parent = None

        return max_move

    def playout(self, state: State):
        """ 1. Select한다. """
        node = self.root
        for d in range(MAX_PLAYOUT_DEPTH):
            if node.is_leaf():
                # Leaf라면 방문하지 않은 노드이다. 2. Expand한다.
                policies = sample_from_policy(state)

                if len(policies) == 0:
                    # end of game
                    # TODO: 이걸로 break시킬것인가 아니면 state를 통해 break시킬것인가?
                    break

                # dbg.log(' Policy : {}'.format(policies))
                node.expand(policies)

            # go deeper
            action, node = node.select()
            state.do(action)

        # 하드코딩한 승률과 시뮬레이션 상 승률을 조합함.
        winrate = get_winrate(state)
        simulated_winrate = self.rollout(state)
        # value = (1-LAMBDA)*winrate + LAMBDA*simulated_winrate
        value = simulated_winrate

        # 4. Backpropagate
        node.backpropagate(value)

    def rollout(self, state: State) -> float:
        global win_count, draw_count, fail_count

        """ 3. Simulation. state는 copy안하고 레퍼런스로 가져간다 - 이젠 수정해도됨. """
        for d in range(MAX_ROLLOUT_DEPTH / 2):
            move1, move2 = sample_two_from_rollout_policy(state)
            if move1 is None: break
            state.do(move1)

            if move2 is None: break
            state.do(move2)

        # simulation result.
        if state.winner == 1:
            win_count += 1
            return 1
        elif state.winner == 0:
            draw_count += 1
            return 0
        else:
            fail_count += 1
            return -1


class State:
    def __init__(self, board=[[0 for x in range(19)] for y in range(19)], nth_move=0):
        self.board = board
        self.player = 1  # 삼성 코드기준으로 나는 항상 1임.
        self.turn_count = 0
        self.nth_move = nth_move

        self.search_space = []
        self.search_space_mark = [[0 for x in range(19)] for y in range(19)] # int{}{}. TODO: BLOCKED 반영!!!
        self.last_enemy_moves = []

        self.referee = Referee(board)  # TODO: only for python!!
        self.winner = 0

    def copy(self):
        new_board = memcpy(self.board, BOARD_SIZE)
        new_state = State(new_board, self.nth_move)
        new_state.search_space_mark = memcpy(self.search_space_mark, BOARD_SIZE)
        new_state.search_space = self.search_space
        new_state.turn_count = self.turn_count
        new_state.player = self.player

    def do(self, move: Point):
        self.board[move.y][move.x] = self.player
        self.referee.update(move.x, move.y, self.player)
        self.expand_search_space(move)

        self.turn_count += 1
        if self.turn_count == 2:
            # change turn.
            self.turn_count = 0
            self.player = 2 if self.player == 1 else 1
            self.nth_move += 1

    def do_enemy(self, point):
        self.player = 2
        self.last_enemy_moves.append(point)
        self.do(point)
        self.player = 1

    def update_enemy_board(self, board, nth_move):
        self.nth_move = nth_move
        self.last_enemy_moves.clear()

        # 상대편이 수를 둔 후의 보드를 업데이트한다. O(N^2).
        for y in range(19):
            for x in range(19):
                if self.board[y][x] != board[y][x]:
                    point = Point(x,y)
                    self.do_enemy(point)

        # 이제 my turn이 된다.
        self.player = 1
        self.turn_count = 0

    def has_winner(self):
        won_player = self.referee.determine()
        if won_player:
            self.winner = won_player
            return True
        return False


    def expand_search_space(self, p: Point):
        # expand search space
        for dx, dy in SEARCH_SPACE_DIRECTIONS:
            nx, ny = p.x+dx, p.y+dy
            if self.search_space_mark[ny][nx] == 0:
                self.search_space.append(Point(nx, ny))
                self.search_space_mark[ny][nx] = 1

        # Cannot place in already placed area.
        self.search_space_mark[p.y][p.x] = -1


    def can_search(self, point):
        return self.search_space_mark[point.y][point.x] == 1


    def distance_factor(self, your_move):
        sum = 0.0
        for p in self.last_enemy_moves:
            sum += distance(your_move, p)

        return 1 - 0.7 * sum / len(self.last_enemy_moves)



def sample_from_policy(state: State, player=1):
    """ 어떤 수를 둬야할지 결정한다. """
    policies = []
    for point in state.search_space:
        if not state.can_search(point): continue

        # TODO: evaluate value
        value = random.uniform(0, 1)

        policy_value = value * state.distance_factor(point)
        policies.append((point, policy_value))

    return policies

def get_winrate(state: State) -> float:
    # if state.has_winner()
    # TODO: implement
    return 0


def sample_two_from_rollout_policy(state: State) -> Point:
    # if state.player == 1:
    #
    #
    # elif state.player == 2:
    #

    strstats = scan_full(state.board)
    enemy_strstats = strstats[1] if state.player == 1 else strstats[0]
    my_strstats = strstats[0] if state.player == 1 else strstats[1]

    if enemy_strstats.a > 0:
        # 체크 - 무슨 수를 써서라도 막음
        return enemy_strstats.a_point.pop()

    elif enemy_strstats.b > 0:
        # 덜 위험한 체크 - 남은 수를 준다
        return enemy_strstats.b_point.pop()

    # TODO: implement!
    return random.choice(state.search_space)



mcts = MCTS()
state = State()

def samsung_like_move(board, nth_move):
    state.update_enemy_board(board, nth_move)

    # TODO: cnt는 c로 옮기지 마시오.
    cnt = 2
    if nth_move == 1:
        state.turn_count = 1
        cnt = 1  # 1번만 돌아야함.

    moves = []
    for _ in range(cnt):
        move = mcts.move(state)
        moves += move
        state.do(move)

    dbg.log('Win: {} Draw: {} Fail: {}'.format(win_count, draw_count, fail_count))
    dbg.stop()

    return moves

def distance(p1, p2):
    # chebyshev distance.
    return max(abs(p2.y - p1.y), abs(p2.x - p1.x))
