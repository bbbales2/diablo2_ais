import random
import replayer
import numpy
import time
import json
import keras

cx = 325
cy = 237
r = 50

class Ai(replayer.Ai):
    def __init__(self, logFileName, dataFile):
        with open(dataFile, 'r') as f:
            dataFile = json.load(f)
        self.model = keras.models.load_model(dataFile['kerasModel'])
        self.mix = dataFile['mix']
        self.lastAction = time.time()
        super(Ai, self).__init__(logFileName, dataFile["replayFile"])
        
    def go(self, state):
        if self.replaying:
            action = self.replay()
            return action 

        if time.time() - self.lastAction > 0.5 and state is not None:
            rewards = []
            for i in range(8):
                x = numpy.zeros((1, 10))
                x[0, 0] = state['x'] - 4863
                x[0, 1] = state['y'] - 5653
                x[0, 2 + i] = 1
                rewards.append(self.model.predict(x)[0, 0])

            angles = [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0]

            angleI = random.randint(0, len(angles) - 1) if random.random() < self.mix else numpy.argmax(rewards)
            
            print rewards

            x = cx + numpy.cos(angles[angleI]) * 50
            y = cy - numpy.sin(angles[angleI]) * 50 # Coordinate system is backwards
            
            action = (1, x, y)
            self.lastAction = time.time()
            self.logAction(state, angleI)
        else:
            action = (0, 0, 0)

        self.first = False
        return action
