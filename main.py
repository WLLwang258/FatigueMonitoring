import cv2

from face_detect import FaceDetect
from shell_config_parse import ShellConfigParser

def main():
    args = ShellConfigParser().get_args()
    face_detector = FaceDetect(args)


if __name__ == '__main__':
    main()
