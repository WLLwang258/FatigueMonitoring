from face_detect import FaceDetect
from shell_config_parse import ShellConfigParser

def main():
    face_detector = None
    args = ShellConfigParser().get_args()
    try:
        face_detector = FaceDetect(args)
    except FileNotFoundError:
        face_detector.file_operations.log_program_start(False)
    except Exception as e:
        face_detector.file_operations.log_error(e)

if __name__ == '__main__':
    main()
