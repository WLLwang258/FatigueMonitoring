import argparse

class ShellConfigParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-i", "--image", required=False, help="path to image")
        self.parser.add_argument("-p", "--predictor", required=True, help="path to shape_predictor")
        self.parser.add_argument("-v", "--video", required=True, help="path to detect video")
        self.args = vars(self.parser.parse_args())
        if self.args["image"] and self.args["video"]:
            print("cannot use both --image and --video")
            exit(1)

    def get_args(self):
        return self.args