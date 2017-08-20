import random
import time
import json
import pygame

class Ai(object):
    def __init__(self, logFileName, replayFileName):
        self.first = True
        
        self.logFileName = logFileName
        if replayFileName is not None:
            self.replayFile = open(replayFileName)
            self.replaying = True
        else:
            self.replaying = False

        open(self.logFileName, "w").close()
        return

    def handle(self, e):
        if e.type == pygame.locals.MOUSEBUTTONUP:
            if e.button == 1:
                self.logAction((1, e.pos[0], e.pos[1]))
            if e.button == 4:
                self.logAction((2, e.pos[0], e.pos[1]))

    def replay(self):
        if self.first:
            self.replayLine = json.loads(self.replayFile.readline())
            t, (click, x, y) = self.replayLine 
            self.replay_offset = time.time() - t

        if self.replayLine == None:
            line = self.replayFile.readline()
            if line.strip() == "":
                self.replaying = False
                return (0, 0, 0)
            else:
                self.replayLine = json.loads(line)

        t, (click, x, y) = self.replayLine
        if time.time() > self.replay_offset + t:
            action = (click, x, y)
            self.replayLine = None
        else:
            action = (0, 0, 0)

        self.first = False
        return action

    def go(self):
        if self.replaying:
            return self.replay()

        self.first = False
        return (0, 0, 0)

    def logAction(self, action):
        with open(self.logFileName, "a") as f:
            f.write(json.dumps((time.time(), action)) + "\n")
