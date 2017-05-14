#!/usr/bin/env python3
import os
from common import Point
from logger import MoveLogger
from rules import Referee
from bot import Bot
from config import AIBot

# constants
STONE_CHAR = ['.', 'O', 'X']
STONE_NAME = ['', 'White (O)', 'Black (X)']
CHAR_TO_X = {chr(ord('A') + i) : i for i in range(19)}
X_TO_CHAR = {i: chr(ord('A')+i) for i in range(19)}

# console helper methods
def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

def darktext(str):
    return str if os.name == 'nt' else '\x1b[0;30m{}\x1b[0m'.format(str)


def draw_board(board, player=0, nth_move=0):
    cls()
    print('Move : {}'.format(nth_move))
    print('{} turn.'.format(STONE_NAME[player]))
    print()
    print('       A B C D E F G H I J K L M N O P Q R S ')
    print('     +---------------------------------------+')
    
    for y in range(19):
        print('  {:>2d} |'.format(y+1), end='')  # line no.
        for x in range(19):
            stone = board[y][x]
            if stone != 0: print(' ' + STONE_CHAR[board[y][x]], end='')
            else: print(darktext(' '+X_TO_CHAR[x].lower()), end='')
        print(' |')

    print('     +---------------------------------------+')
    print()


class Player(Bot):
    """ 플레이어도 봇으로 취급하지만, 사용자로부터 입력을 받음. """

    def move(self, board, nth_move):
        move = input('{} turn : '.format(STONE_NAME[self.player]))
        return Point.from_name(move)


def exit_game(logger: MoveLogger, won_bot=None):
    if won_bot is not None:
        logger.log_winner(won_bot.player)
        print('{} ({}) won!!'.format(STONE_NAME[won_bot.player], won_bot.bot_kind))
    else:
        print('No one won.')

    logger.save_to_file()


def main(bots):
    # to align index with player variable.
    bot_set = [None] + bots

    board = [[0 for x in range(19)] for y in range(19)]
    referee = Referee(board)

    nth_move = 1
    player = 2  # 1=white 2=black. black moves first
    player_moved_count = 1  # at first time, black can only move once.
    logger = MoveLogger()

    while True:
        draw_board(board, player, nth_move)
        
        # input loop.
        while True:
            try:
                x, y = bot_set[player].move(board, nth_move)
                able_to_place, msg = referee.can_place(x, y)
                if not able_to_place:
                    print('{}. Try again in another place.'.format(msg))
                    continue
                break

            except KeyboardInterrupt:
                print('\n' + 'Bye...')
                exit_game(logger)
                return

            except:
                print('Wrong input.')
                continue

        # place stone
        board[y][x] = player
        logger.log(x, y, player)
        referee.update(x, y, player)

        won_player = referee.determine()
        if won_player is not None:
            exit_game(logger, bot_set[won_player])
            return

        player_moved_count += 1
        if player_moved_count == 2:
            # Change turn : a player can move 2 times per turn.
            nth_move += 1
            player_moved_count = 0
            player = 2 if player == 1 else 1


if __name__ == '__main__':
    print('Welcome to TherneConnect6.')
    print('Choose player slot. (1=Player 2=AI)')

    black_choice = input(' Black (1 or 2) : ')
    white_choice = input(' White (1 or 2) : ')

    whitebot = Player(1) if white_choice == '1' else AIBot(1)
    blackbot = Player(2) if black_choice == '1' else AIBot(2)

    main([whitebot, blackbot])
