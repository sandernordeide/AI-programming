from game import HexGame
from mcts import MonteCarloTreeSearch
from ANN import ANN
import random
from tqdm import tqdm
import math
import numpy as np
from matplotlib import pyplot as plt
np.set_printoptions(linewidth=160) # print formatting

def RL_algorithm(games, simulations, env, ANN, eps_decay, epochs):
    cases = [[],[]]
    MCTS = MonteCarloTreeSearch(ANN)
    for i in tqdm(range(games)):
        env.reset()
        MCTS.init_tree()
        M = simulations
        while not env.is_game_over():
            action, D = MCTS.search(env, M)
            cases[0].append(env.flat_state)
            cases[1].append(D)
            env.move(action)
            #M = math.ceil(M*0.8)
        fit_cases = list(zip(cases[0],cases[1]))
        fit_cases = random.sample(fit_cases, math.ceil(len(cases[0])/2))
        ANN.fit(list(zip(*fit_cases)))
        ANN.epochs += math.floor(np.exp(i*3/(games)))
        #if (i+1) % save_interval == 0:
        #    ANN.model.save_weights(model_path.format(level=i+1))

    ANN.epochs = 1
    accuracies = []
    epochs = []
    split = math.floor(len(cases[0])/10)
    val_data = [cases[0][0:split], cases[1][0:split]] #10% of data is validation data
    train_data = list(zip(cases[0][split:len(cases[0])],cases[1][split:len(cases[1])]))
    print("fitting")
    for epoch in tqdm(range(1000)):
        random.shuffle(train_data)
        ANN.fit(list(zip(*train_data)))
        acc = ANN.accuracy(val_data)
        accuracies.append(acc)
        epochs.append(epoch)

    print("terminated after epoch number", epoch)
    plt.plot(epochs, accuracies)
    plt.show()
    return ANN.make_dict(cases)


def play_game(dict, env, ANN, delay=-1,verbose=True):
    env.reset()
    inputs = []
    moves = []
    preds = []
    j = 0
    while not env.is_game_over():
        inputs.append(env.flat_state)
        probs, action = ANN.get_move(env)
        if verbose:
            print()
            input = tuple(env.flat_state)
            print(input)
            if dict.get(input) != None:
                targets = []
                for tar, _ in dict[input]:
                    targets.append(tar)
                mean_target = np.around(np.mean(targets, axis = 0),decimals = 1)
                print(mean_target)
            else:
                print("No such case for input state")
            print(np.around(probs.numpy()*100, decimals = 1))
            if delay > -1:
                env.draw()
        else:
            if delay > -1:
                env.draw(delay)
        preds.append(np.around(probs.numpy()*100, decimals = 1))
        moves.append(action)
        env.move(action)
        j += 1
    winning_player =  3 - env.flat_state[0]
    print("player", winning_player, "won after", j, "moves.")
    if delay > -1:
        env.draw()


def say():
    import os
    os.system('say "gamle ørn, jeg er ferdig  "')

def generate_cases(games, simulations, env):
    cases = [[],[]]
    MCTS = MonteCarloTreeSearch()
    for i in tqdm(range(games)):
        env.reset()
        MCTS.init_tree()
        M = simulations
        while not env.is_game_over():
            action, D = MCTS.search(env, M)
            cases[0].append(env.flat_state)
            cases[1].append(D)
            env.move(action)
    return cases

def train_ann(inputs, targets, ANN):
    ANN.epochs = 1
    accuracies = []
    epochs = []
    split = math.floor(len(inputs)/10)
    val_data = [inputs[0:split], targets[0:split]] #10% of data is validation data
    train_data = list(zip(inputs[split:len(inputs)],targets[split:len(targets)]))
    print("fitting")
    for epoch in tqdm(range(1000)):
        random.shuffle(train_data)
        ANN.fit(list(zip(*train_data)))
        acc = ANN.accuracy(val_data)
        accuracies.append(acc)
        epochs.append(epoch)

    print("terminated after epoch number", epoch)
    plt.plot(epochs, accuracies)
    plt.show()

def write_db(filename, object):
    np.savetxt(filename, object)

def load_db(filename):
    return np.loadtxt(filename)

if __name__ == '__main__':
    # Game parameters
    board_size = 6
    env = HexGame(board_size)

    # MCTS/RL parameters
    episodes = 1000
    simulations = 500

    #training_batch_size = 100
    ann_save_interval = 10
    eps_decay = 1

    # ANN parameters
    activation_functions = ["linear", "sigmoid", "tanh", "relu"]
    optimizers = ["Adagrad", "SGD", "RMSprop", "Adam"]
    alpha = 0.005 # learning rate
    H_dims = [board_size*board_size]
    io_dim = board_size * board_size # input and output layer sizes (always equal)
    activation = activation_functions[3]
    optimizer = optimizers[3]
    epochs = 1
    ann = ANN(io_dim, H_dims, alpha, optimizer, activation, epochs)

    #cases = generate_cases(episodes, simulations, HexGame(board_size))
    #inputs = cases[0]
    #targets = cases[1]
    #write_db( , inputs)
    #write_db( , targets)

    inputs = load_db("size_four_inputs.txt")
    targets = load_db("size_four_targets.txt")
    train_ann(inputs,targets,ann)
    def play(dict = pred_dict, env = env, ANN = ann):
        play_game(dict, env,ann,-1,0)
    play()
    """
    for i in range(1):
        print(i)
        pred_dict = RL_algorithm(episodes, simulations, env, ann, eps_decay, epochs)

        play()
    """


    #import pdb; pdb.set_trace()
