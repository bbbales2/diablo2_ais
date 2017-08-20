import random
import time
import json
import pygame

class Ai(object):
    def __init__(self, logFileName, replayFileName):
        self.logFileName = logFileName
        self.replayFileName = replayFileName
        open(self.logFileName, "w").close()
        return

    def handle(self, e):
        if e.type == pygame.locals.MOUSEBUTTONUP:
            if e.button == 1:
                self.logAction((1, e.pos[0], e.pos[1]))
            if e.button == 4:
                self.logAction((2, e.pos[0], e.pos[1]))

    def logAction(self, action):
        with open(self.logFileName, "a") as f:
            f.write(json.dumps((time.time(), action)) + "\n")
