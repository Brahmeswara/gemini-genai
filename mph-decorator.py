from controller import Controller
import os

fw = Controller(os.getenv('CONFIG_FILE'))
fw.targetSetup() 