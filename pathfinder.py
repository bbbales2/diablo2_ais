import random
import replayer
import numpy
import time
import json
import keras
import pygame

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

        if "saveLayer" in dataFile and self.model:
            self.saveLayer = keras.models.Model(inputs = self.model.input,
                                                outputs = self.model.layers[dataFile["saveLayer"]].output)
        else:
            self.saveLayer = None

        self.color = (255, 0, 0)
        self.direction = numpy.random.randint(0, 7)
        self.lastMoved = 0.0
        self.lastClicked = 0.0
        self.lastChangedDirection = 0.0
        self.lastPosition = numpy.array([0.0, 0.0])
        self.lastAction = time.time()
        super(Ai, self).__init__(logFileName, dataFile["replayFile"])
        
    def go(self, state, screen):
        if self.replaying:
            action = self.replay()
            return action 

        if state is not None and \
           (state['x'] != 0 and state['y']) and \
           state['mode'] in (1, 4, 5):
            angles = [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0]
            position = numpy.array([state['x'], state['y']])

            if state['lastUnitClicked']:
                self.lastClicked = time.time()
            
            if numpy.linalg.norm(position - self.lastPosition) != 0:
                self.lastMoved = time.time()

            if (time.time() - self.lastChangedDirection) > 15.0 or ((time.time() - self.lastMoved) > 2.0 and (time.time() - self.lastClicked) > 2.0):
                self.direction = numpy.random.randint(0, 7)
                self.lastChangedDirection = time.time()

            if self.model and random.random() > self.mix:
                xv = state['x']
                yv = state['y']
                rewards = []
                for i in range(8):
                    x = numpy.zeros((1, 8))
                    x[0, i] = 1
                    rewards.append(self.model.predict([state['screen'].reshape((1, 400, 640, 3))[:, :, :, :], x])[0, 0])

                rewards = numpy.array(rewards)

                #p = softmax(rewards)
                #angleI = numpy.random.choice(range(8), p = p)
                
                #print rewards
                if max(rewards) > 1.5:
                    angleI = numpy.argmax(rewards)
                    self.color = (0, 255, 0)
                    print "Picking!"
                else:
                    angleI = self.direction
                    self.color = (255, 0, 0)

                if numpy.random.random() < 0.05:
                    button = 2
                elif numpy.random.random() < 0.05:
                    button = 49
                else:
                    button = 1

                print ' '.join('{0:3.1f}'.format(x) for x in rewards)
                #print ' '.join('{0:.2f}'.format(x) for x in p)
                #print angleI, angles[angleI]
            else:
                angleI = self.direction
                button = 1

            x = cx + numpy.cos(numpy.pi * angles[angleI] / 180.0) * r
            y = cy - numpy.sin(numpy.pi * angles[angleI] / 180.0) * r # Coordinate system is backwards

            self.lastPosition = position

            action = (button, x, y)
            self.lastAction = time.time()

            if self.saveLayer:
                x = numpy.zeros((1, 8))
                state['layer'] = self.saveLayer.predict([state['screen'].reshape((1, 400, 640, 3))[:, :, :, :], x]).flatten().tolist()
                del state['screen']
            self.logAction(state, (button, angleI))
        else:
            action = (0, 0, 0)

        pygame.draw.circle(screen, self.color, (700, 100), 10, 0)
            
        self.first = False
        return action
    
