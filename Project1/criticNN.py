import math
import tensorflow as tf
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import pdb


# ************** Split Gradient Descent (SplitGD) **********************************
# This "exposes" the gradients during gradient descent by breaking the call to "fit" into two calls: tape.gradient
# and optimizer.apply_gradients.  This enables intermediate modification of the gradients.  You can find many other
# examples of this concept online and in the (excellent) book "Hands-On Machine Learning with Scikit-Learn, Keras,
# and Tensorflow", 2nd edition, (Geron, 2019).

# This class serves as a wrapper around a keras model.  Then, instead of calling keras_model.fit, just call
# SplitGD.fit.  To use this class, just subclass it and write your own code for the "modify_gradients" method.

class CriticNN:

    def __init__(self, alpha, lam, gamma, inputDim=0, nodesInLayers=[0]):
        self.alpha = alpha
        self.lam = lam
        self.gamma = gamma
        self.surprise = 0
        self.eligibilities = []
        self.model = Sequential()
        self.model.add(
            Dense(nodesInLayers[0], activation='hard_sigmoid', input_dim=inputDim))
        for i in range(1, len(nodesInLayers)):
            self.model.add(Dense(nodesInLayers[i], activation='hard_sigmoid'))
        self.resetEligibilities()
        #sgd = tf.train.GradientDescentOptimizer(learning_rate = alpha)
        sgd = tf.optimizers.SGD(lr=alpha)
        self.model.compile(optimizer=sgd, loss='mse')
        #keras.utils.plot_model(self.model, show_shapes = True)

    def resetEligibilities(self):
        for params in self.model.trainable_weights:
            self.eligibilities.append(tf.zeros_like(params))

    def findTDError(self, reinforcement, lastState, state):
        # converting states from string to tensor
        lastState = [tf.strings.to_number(bin, out_type=tf.dtypes.float32) for bin in lastState]  # convert to array
        state = [tf.strings.to_number(bin, out_type=tf.dtypes.float32) for bin in state]
        lastState = tf.convert_to_tensor(np.expand_dims(lastState, axis=0))
        state = tf.convert_to_tensor(np.expand_dims(state, axis=0))

        gamma = tf.convert_to_tensor(self.gamma, dtype=tf.dtypes.float32)
        reinforcement = tf.convert_to_tensor(reinforcement, dtype=tf.dtypes.float32)

        tensor_model = tf.function(func=self.model)
        td_error = tf.subtract(tf.add(reinforcement, tf.multiply(gamma, tensor_model(state))),tensor_model(lastState)).numpy()[0][0]
        #self.fit(lastState, target)

        #tensor_model = tf.function(func=self.model)
        #prediction = tensor_model(lastState)
        #print("prediction fitNN", prediction.numpy())

        return td_error

    # Subclass this with something useful.

    def modify_gradients(self, gradients, loss, td_error):
        #print("tdError", loss.numpy())
        alpha = tf.convert_to_tensor(self.alpha, dtype=tf.dtypes.float32)
        for i in range(len(gradients)):
            # print(self.eligibilities[i].numpy())

            self.eligibilities[i] = tf.add(self.eligibilities[i], gradients[i])
            #gradients[i] = tf.multiply(alpha, tf.multiply(tdError, self.eligibilities[i]))

            gradients[i] = self.eligibilities[i] * td_error
            # print()
        return gradients

    # This returns a tensor of losses, OR the value of the averaged tensor.  Note: use .numpy() to get the
    # value of a tensor.
    def gen_loss(self, lastState, td_error):
        #print("in genloss")
        tensor_model = tf.function(func=self.model)
        prediction = tensor_model(lastState)
        target = tf.add(td_error, prediction)
        #print("prediction genloss", prediction.numpy())
        loss = self.model.loss_functions[0](target, prediction)
        return loss

    def fit(self, td_error, lastState, verbose=True):
        lastState = [tf.strings.to_number(bin, out_type=tf.dtypes.float32) for bin in lastState]  # convert to array
        lastState = tf.convert_to_tensor(np.expand_dims(lastState, axis=0))
        #tensor_model = tf.function(func=self.model)
        #prediction = tensor_model(lastState)
        params = self.model.trainable_weights
        with tf.GradientTape() as tape:
            loss = self.gen_loss(lastState, td_error)
            tape.watch(loss)
            gradients = tape.gradient(loss, params)
            gradients = self.modify_gradients(gradients, loss, td_error)
            #gradients = tf.Variable(gradients)
            #params = tf.Variable(params)
            #grads_and_vars = zip(gradients, params)
            # print(type(gradients))
            #print(type(self.model.optimizer))
            self.model.optimizer.apply_gradients(zip(gradients, params))
            # self.model.optimizer.apply_gradients(grads_and_vars)
            # self.model.apply_gradients(zip(gradients,params))
        #if verbose: self.end_of_epoch_display(train_ins,train_targs,val_ins,val_targs)

    # Use the 'metric' to run a quick test on any set of features and targets.  A typical metric is some form of
    # 'accuracy', such as 'categorical_accuracy'.  Read up on Keras.metrics !!
    # Note that the model.metrics__names slot includes the name of the loss function (as 0th entry),
    # whereas the model.metrics slot does not include the loss function, hence the index+1 in the final line.
    # Use your debugger and go through the long list of slots for a keras model.  There are a lot of useful things
    # that you have access to.

    def gen_evaluation(self, features, target, avg=False, index=0):
        predictions = self.model(features)
        evaluation = self.model.metrics[index](targets, predictions)
        #  Note that this returns both a tensor (or value) and the NAME of the metric
        return (tf.reduce_mean(evaluation).numpy() if avg else evaluation, self.model.metrics_names[index + 1])

    def status_display(self, features, targets, mode='Train'):
        print(mode + ' *** ', end='')
        print('Loss: ', self.gen_loss(features, targets, avg=True), end=' : ')
        val, name = self.gen_evaluation(features, targets)
        print('Eval({0}): {1} '.format(name, val))

    def end_of_epoch_display(self, train_ins, train_targs, val_ins, val_targs):
        self.status_display(train_ins, train_targs, mode='Train')
        if len(val_ins) > 0:
            self.status_display(val_ins, val_targs, mode='      Validation')

# A few useful auxiliary functions


def gen_random_minibatch(inputs, targets, mbs=1):
    indices = np.random.randint(len(inputs), size=mbs)
    return inputs[indices], targets[indices]

# This returns: train_features, train_targets, validation_features, validation_targets


def split_training_data(inputs, targets, vfrac=0.1, mix=True):
    vc = round(vfrac * len(inputs))  # vfrac = validation_fraction
    # pairs = np.array(list(zip(inputs,targets)))
    if vfrac > 0:
        pairs = list(zip(inputs, targets))
        if mix:
            np.random.shuffle(pairs)
        vcases = pairs[0:vc]
        tcases = pairs[vc:]
        return np.array([tc[0] for tc in tcases]), np.array([tc[1] for tc in tcases]),\
            np.array([vc[0] for vc in vcases]), np.array([vc[1]
                                                          for vc in vcases])
        #  return tcases[:,0], tcases[:,1], vcases[:,0], vcases[:,1]  # Can't get this to work properly
    else:
        return inputs, targets, [], []
