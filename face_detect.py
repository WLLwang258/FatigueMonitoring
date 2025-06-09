import dlib
import cv2
from constants import *
from file_operations import FileOperations
from utils import shape_to_np, get_eye_aspect_ratio

def preprocess_roi(roi):
    """
    return roi
    """
    (h, w) = roi.shape[:2]
    width = IMAGE_RESIZE_WIDTH
    ratio = width / float(w)
    dim = (width, int(h * ratio))
    roi = cv2.resize(roi, dim, interpolation=cv2.INTER_AREA)
    return roi


def preprocess_frame(origin_frame, resize_width):
    """
    Preprocess the input frame.
    """
    h, w = origin_frame.shape[:2]
    width = resize_width
    ratio = width / float(w)
    dim = (width, int(h * ratio))
    frame_preprocessed = cv2.resize(origin_frame, dim, interpolation=cv2.INTER_AREA)
    frame_gray = cv2.cvtColor(frame_preprocessed, cv2.COLOR_BGR2GRAY)
    return frame_preprocessed, frame_gray


class FaceDetect:
    def __init__(self, args):
        self.file_operations = FileOperations()

        self.frame = None
        self.gray = None
        self.faces = None
        self.landmarks = None
        self.vid = None

        self.blinks_counter = 0
        self.counter = 0
        self.is_long_term_closed = False
        self.counter_ = 0

        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(args["predictor"])
        if args["image"]:
            self.__preprocess_frame_by_img(args["image"])
        elif args["video"]:
            self.__video_detect(args["video"])

    def __preprocess_frame_by_img(self, img_src):
        """
        preprocess current frame, resize frame, get gray
        """
        try:
            self.frame = cv2.imread(img_src)
            if self.frame is None:
                raise FileNotFoundError(f"The image at path '{img_src}' does not exist or cannot be read.")
            self.frame, self.gray = preprocess_frame(self.frame, IMAGE_RESIZE_WIDTH)
        except FileNotFoundError as e:
            print(f"Error: {e}")
            exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            exit(1)

    def __detect_face_with_current_frame(self):
        """
        get landmarks and rois from current frame
        """
        rects = self.detector(self.gray, 1)
        for (idx, rect) in enumerate(rects):
            shape = self.predictor(self.gray, rect)
            self.landmarks = shape_to_np(shape)

    def __detect_blinks(self):
        (left_eye_start, left_eye_end) = FACIAL_LANDMARKS_68_IDS["left_eye"]
        (right_eye_start, right_eye_end) = FACIAL_LANDMARKS_68_IDS["right_eye"]
        left_eye = self.landmarks[left_eye_start:left_eye_end]
        right_eye = self.landmarks[right_eye_start:right_eye_end]
        left_ear = get_eye_aspect_ratio(left_eye)
        right_ear = get_eye_aspect_ratio(right_eye)
        ear = (left_ear + right_ear) / 2.0

        cv2.putText(self.frame, "EAR: {:.2f}".format(ear), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        left_eye_hull = cv2.convexHull(left_eye)
        right_eye_hull = cv2.convexHull(right_eye)
        cv2.drawContours(self.frame, [left_eye_hull], -1, (0, 255, 0), 1)
        cv2.drawContours(self.frame, [right_eye_hull], -1, (0, 255, 0), 1)

        if ear < EAR_THRESHOLD:
            self.counter += 1
            if self.counter >= BLINKS_THRESHOLD:
                self.is_long_term_closed = True
        else:
            if self.counter >= EAR_GAP_FRAMES:
                self.blinks_counter += 1
            self.counter = 0

            if self.is_long_term_closed:
                self.counter_ += 1
                if self.counter_ >= BLINKS_THRESHOLD:
                    self.counter = 0
                    self.file_operations.log_fatigue_recovery()
                    self.is_long_term_closed = False

        cv2.putText(self.frame, "Blinks: {}".format(self.blinks_counter), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(self.frame, "IsTired: {}".format(self.is_long_term_closed), (200, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(self.frame, "press 'q' quit".format(self.is_long_term_closed), (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


    def __video_detect(self, video_src):
        try:
            self.vid = cv2.VideoCapture(video_src)
            if self.vid is None:
                raise FileNotFoundError(f"The video at path '{video_src}' does not exist or cannot be read.")
            while True:
                new_frame = self.vid.read()[1]
                if new_frame is None:
                    break
                self.frame, self.gray = preprocess_frame(new_frame, VIDEO_RESIZE_WIDTH)
                self.__detect_face_with_current_frame()
                self.__detect_blinks()
                if self.is_long_term_closed:
                    self.file_operations.log_fatigue_detection("长期闭眼")
                cv2.imshow("Video", self.frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except FileNotFoundError as e:
            print(f"Error: {e}")
            exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            exit(1)

    def get_face_with_landmarks(self, colors = None, alpha = 0.75):
        if self.landmarks is None:
            self.__detect_face_with_current_frame()

        overlay = self.frame.copy()
        output = self.frame.copy()

        if colors is None:
            colors = [(19,199,109), (79,76,240), (230,159,23), (168,100,168), (158,163,32), (163,38,32), (180,42,220)]

        for (i, name) in enumerate(FACIAL_LANDMARKS_68_IDS.keys()):
            (j, k) = FACIAL_LANDMARKS_68_IDS[name]
            pts = self.landmarks[j:k]
            if name == "jaw":
                for l in range(1, len(pts)):
                    pt_a = tuple(pts[l - 1])
                    pt_b = tuple(pts[l])
                    cv2.line(overlay, pt_a, pt_b, colors[i], 2)
            else:
                hull = cv2.convexHull(pts)
                cv2.drawContours(overlay, [hull], -1, colors[i], -1)
        cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
        return output

    def __del__(self):
        self.vid.release()
        cv2.destroyAllWindows()