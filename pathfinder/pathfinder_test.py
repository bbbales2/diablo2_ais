#%%
from numpy import concatenate, pi, arctan2, array, linalg
import numpy
import json
import keras
import os
import matplotlib.pyplot as plt

os.chdir('/home/bbales2/diablo2_ais/pathfinder')

Xs = []
rewards = []
def process(filename):
    states = []
    actions = []
    with open(filename, "r") as f:
        for line in f:
            if line.strip() != '':
                time, state, action = json.loads(line)
                if state is not None and (state['x'] != 0 and state['y'] != 0):
                    states.append([state['x'], state['y']])
                    actions.append(action)
                    #data.append((time, state, action))

    states = numpy.array(states)
    states -= states[0]

    v1 = linalg.norm(states - [0.0, 0.0], axis = 1)
    v1[v1 > 20.0] = 20.0
    values = -linalg.norm(states - [-200.0, 150.0], axis = 1) + v1
    rewards = values[1:] - values[:-1]
    for i in range(len(rewards)):
        for j in range(i + 1, min(len(rewards), i + 10)):
            rewards[i] += 0.8 ** (j - i) * rewards[j]
        #rewards[i] = min(50.0, rewards[i])

    states = states[:-1]
    actions = actions[:-1]
    X2 = numpy.zeros((len(actions), 8)).astype('int')
    for i in range(len(actions)):
        X2[i, actions[i]] = 1

    X = concatenate((states, X2), axis = 1)

    return X, rewards

for r in ['1', '2', '3', '4', '5', '6']:
    for i in range(60):
        try:
            filename = "../../diablo2_bot_manager/output{1}/{0}.log".format(i, r)
            X, reward = process(filename)

            Xs.append(X)
            rewards.append(reward)
        except:
            break

X = concatenate(Xs, axis = 0)
rewards = concatenate(rewards, axis = 0)
#X = concatenate((states, actions), axis = 1)
plt.plot(X[:, 0], X[:, 1], '*')
plt.axes().set_aspect('equal', 'datalim')
#%%

from keras.models import Sequential
from keras.layers import Dense, Activation
from keras import regularizers, losses

model = Sequential([
  Dense(25, input_shape=(10,), kernel_regularizer = regularizers.l2(0.01)),
  Activation('relu'),
  Dense(15, kernel_regularizer = regularizers.l2(0.01)),
  Activation('relu'),
  Dense(10, kernel_regularizer = regularizers.l2(0.01)),
  Activation('relu'),
  Dense(1, kernel_regularizer = regularizers.l2(0.01)),
])
#model.compile(optimizer='rmsprop',
#              loss='categorical_crossentropy',
#              metrics=['accuracy'])
model.compile(optimizer = 'adam',
              loss = 'mse')#losses.mean_absolute_error)

#X[:, :2] = 0
#%%

model.fit(X, rewards, epochs = 10000, batch_size = 10000)

#%%

plt.plot(model.predict(X), rewards, '*')
plt.plot(rewards, rewards, 'r-')
plt.axes().set_aspect('equal', 'datalim')

model.save("first.keras")

#%%
x = numpy.zeros((1, 10))
x[0, 7] = 1
model.predict(x)[0, 0]