from game import NIMState, LedgeState
from tree import Node
from mcts import MonteCarloTreeSearch
import random
from tqdm import tqdm

def set_starting_player(P):
    assert P == 1 or P == 2 or P == 3, "You can only choose player option 1, 2 or 3"
    if P == 3:
        return random.choice([1,2])
    return P

def run_batch(G, M, N, K, B, P, game_mode, verbose):
    win = 0
    verbose_message = ""
    for i in tqdm(range(G)):
        initial_player = set_starting_player(P)
        action = Node(NIMState(N, K, initial_player) if game_mode == 0 else LedgeState(B, initial_player))
        verbose_message += "Initial state: {}\n".format(action.game_state)
        iteration = 0
        while not action.is_terminal_node():
            player = action.player
            action = MonteCarloTreeSearch(action).best_action(M)
            iteration += 1
            if verbose:
                verbose_message += "{}: ".format(iteration)
                verbose_message += NIMState.print_move(action.prev_action, player, action.game_state) if game_mode == 0 else LedgeState.print_move(action.prev_action, player, action.parent.game_state)
        verbose_message += "{}: ".format(iteration+1)
        verbose_message += NIMState.print_move(action.game_state, 3-player, 0) if game_mode == 0 else LedgeState.print_move(0, 3-player, action.game_state)
        verbose_message += "Player "+str(3-player)+" won\n\n"
        if initial_player == 3-player:
            win += 1
    if verbose: print(verbose_message)
    print("Starting player won {}/{} ({}%)".format(win, G, 100 * win / G))


if __name__ == '__main__':
    G = 5
    M = 500
    N = 15
    K = 5
    B = [0, 0, 0, 2, 0, 1]
    P = 3
    game_mode = 0 # (0/1): NIM/Ledge
    verbose = True

    run_batch(G, M, N, K, B, P, game_mode, verbose)
    #[print(get_best_action(M,1,B).game_state) for i in range(50)]
