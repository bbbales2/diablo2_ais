import random
import replayer
import numpy
import time
import json
import keras

cx = 325
cy = 245
r = 40

def softmax(v):
    p = numpy.exp(v - v.min())
    return p / sum(p)

class Ai(replayer.Ai):
    def __init__(self, logFileName, dataFile):
        with open(dataFile, 'r') as f:
            dataFile = json.load(f)
        if dataFile['kerasModel']:
            self.model = keras.models.load_model(dataFile['kerasModel'])
        else:
            self.model = None
        self.mix = dataFile['mix']

        self.lastAction = time.time()
        super(Ai, self).__init__(logFileName, dataFile["replayFile"])
        
    def go(self, state):
        if self.replaying:
            action = self.replay()
            return action 

        if time.time() - self.lastAction > 1.0 and \
           state is not None and \
           (state['x'] != 0 and state['y']):
            angles = [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0]

            if self.model and random.random() > self.mix:
                xv = state['x']
                yv = state['y']
                rewards = []
                for i in range(8):
                    x = numpy.zeros((1, 8))
                    x[0, i] = 1
                    rewards.append(self.model.predict([state['screen'].reshape((1, 400, 640, 3))[:, 80:340, 190:450, :], x])[0, 0])

                rewards = numpy.array(rewards)

                p = softmax(rewards)
                angleI = numpy.random.choice(range(8), p = p)
                
                #print rewards
                #if max(rewards) > 1.0:
                #angleI = numpy.argmax(rewards)
                #    print "Picking!"
                #else:
                #    angleI = numpy.random.randint(0, 8 - 1)

                #print ' '.join('{0:3.1f}'.format(x) for x in rewards)
                #print ' '.join('{0:.2f}'.format(x) for x in p)
                #print angleI, angles[angleI]
            else:
                angleI = random.randint(0, len(angles) - 1)

            x = cx + numpy.cos(numpy.pi * angles[angleI] / 180.0) * r
            y = cy - numpy.sin(numpy.pi * angles[angleI] / 180.0) * r # Coordinate system is backwards

            action = (1, x, y)
            self.lastAction = time.time()

            self.logAction(state, angleI)
        else:
            action = (0, 0, 0)

        self.first = False
        return action
