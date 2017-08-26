import os
import random
import time
import json
import pygame
import tempfile
import skimage.io

class Ai(object):
    def __init__(self, logFileName, dataFile):
        self.logFileName = logFileName
        self.outputDirectoryName = os.path.dirname(logFileName)
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
            if state and 'screen' in state:
                fd, filename = tempfile.mkstemp(suffix = '.jpg', dir = self.outputDirectoryName)
                os.close(fd)
                skimage.io.imsave(filename, state['screen'], quality = 99)
                state['screen'] = filename
            f.write(json.dumps((time.time(), state, action)) + "\n")
