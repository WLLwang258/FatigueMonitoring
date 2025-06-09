import numpy as np

def shape_to_np(shape, dtype="int"):
    """
    shape data trans for numpy
    """
    return np.array([(shape.part(i).x, shape.part(i).y) for i in range(shape.num_parts)], dtype=dtype)

def euclidean_distance(point1, point2):
    """
    return the Euclidean distance between two points
    """
    return np.sqrt(np.sum((point1 - point2) ** 2))

def get_eye_aspect_ratio(eye):
    """
    return the Eye Aspect Ratio
    """
    dist_1_5 = euclidean_distance(eye[1], eye[5])
    dist_2_4 = euclidean_distance(eye[2], eye[4])
    dist_0_3 = euclidean_distance(eye[0], eye[3])
    ear = (dist_1_5 + dist_2_4) / (2.0 * dist_0_3)
    return ear

