import numpy as np


class GameState:
    def __init__(self, state, turn=1):
        self.state = state
        self.turn = turn

    @property
    def game_result(self):
        if self.is_game_over():
            return 3-self.turn
        return None

class NIMState(GameState):
    def __init__(self, state, K, turn=1):
        super().__init__(state, turn)
        self.K = K

    def is_game_over(self):
        return self.state == 0

    def move(self, action):
        new_state = np.copy(self.state)
        new_state -= action
        return NIMState(new_state, self.K, 3 - self.turn)

    def get_legal_actions(self):
        return list(range(1, min(self.state, self.K) + 1))

    @staticmethod
    def print_move(node, turn):
        action = node.prev_action
        remaining = "Remaining stones = {:<2}".format(node.state.state)
        stones = "{:<1} stones".format(action) if action > 1 else "{:<2} stone".format(action)
        return "Player {} selects {:>8}: {:>21}\n".format(turn, stones, remaining)


class LedgeState(GameState):
    def __init__(self, state, turn=1):
        super().__init__(state, turn)

    def is_game_over(self):
        return list(self.state).count(2) == 0

    def move(self, action):
        new_board = np.copy(self.state)
        if action == 0:
            assert new_board[0] != 0, 'There is no coin on the ledge'
            new_board[0] = 0
        else:
            i, j = action
            assert new_board[i] != 0, 'There is no coin in spot {}'.format(i)
            assert new_board[j] == 0, 'You cannot put a coin in spot {}'.format(
                j)
            new_board[j] = new_board[i]
            new_board[i] = 0

        return LedgeState(new_board, 3 - self.turn)

    def get_legal_actions(self):
        if self.state[0] == 2: return [0] # make it only possible to pick up gold if possible
        valid = []
        board = self.state
        board_length = len(self.state)
        for i in range(board_length - 1):
            if i == 0 and board[0] != 0:
                valid.append(0)
                continue
            to = []
            if board[i + 1] != 0:
                j = i
                while j >= 0 and board[j] == 0:
                    to.append(j)
                    j -= 1
            [valid.append((i + 1, j)) for j in to]
        return valid

    @staticmethod
    def print_move(node, turn):
        action = node.prev_action
        if action == 0:
            coin = "copper" if node.parent.state.state[0] == 1 else "gold"
            return "P{} picks up {}: {}\n".format(turn, coin, str(node.state.state))
        else:
            coin = "copper" if node.parent.state.state[action[0]] == 1 else "gold"
            return "P{} moves {} from cell {} to {}: {}\n".format(turn, coin, action[0], action[1], str(node.state.state))
