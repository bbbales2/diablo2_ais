import os
import random
import time
import json
import pygame
import tempfile
import skimage.io
import recorder

class Ai(recorder.Ai):
    def __init__(self, logFileName, replayFileName):
        super(Ai, self).__init__(logFileName, None)
        
        self.first = True
        
        if replayFileName is not None:
            self.replayFile = open(replayFileName)
            self.replaying = True
        else:
            self.replaying = False

        return

    def handle(self, e, state):
        if e.type == pygame.locals.MOUSEBUTTONUP:
            if e.button == 1:
                self.logAction(state, (1, e.pos[0], e.pos[1]))
            if e.button == 4:
                self.logAction(state, (2, e.pos[0], e.pos[1]))

    def replay(self):
        if self.first:
            self.replayLine = json.loads(self.replayFile.readline())
            t, action, (click, x, y) = self.replayLine 
            self.replay_offset = time.time() - t

        if self.replayLine == None:
            line = self.replayFile.readline()
            if line.strip() == "":
                self.replaying = False
                return (0, 0, 0)
            else:
                self.replayLine = json.loads(line)

        t, action, (click, x, y) = self.replayLine
        if time.time() > self.replay_offset + t:
            action = (click, x, y)
            self.replayLine = None
        else:
            action = (0, 0, 0)

        self.first = False
        return action

    def go(self, state):
        if self.replaying:
            action = self.replay()
            if action[0] != 0:
                self.logAction(state, action)
            return action 

        self.first = False
        return (0, 0, 0)
