import random
import time
import json
import pygame

class Ai(object):
    def __init__(self, logFileName, dataFile):
        self.logFileName = logFileName
        open(self.logFileName, "w").close()
        return

    def handle(self, e, state):
        if e.type == pygame.locals.MOUSEBUTTONUP:
            if e.button == 1:
                self.logAction(state, (1, e.pos[0], e.pos[1]))
            if e.button == 4:
                self.logAction(state, (2, e.pos[0], e.pos[1]))

    def logAction(self, state, action):
        with open(self.logFileName, "a") as f:
            f.write(json.dumps((time.time(), state, action)) + "\n")
