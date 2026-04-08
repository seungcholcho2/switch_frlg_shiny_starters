from pathlib import Path

import cv2
import numpy as np


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def crop(frame: np.ndarray, roi: tuple[int, int, int, int]) -> np.ndarray:
    x1, y1, x2, y2 = roi
    return frame[y1:y2, x1:x2]


def to_gray(img: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def load_gray_image_or_die(path: Path) -> np.ndarray:
    if not path.exists():
        raise RuntimeError(
            "\n[템플릿 파일 없음]\n"
            f"- 찾은 경로: {path}\n"
            "- 확인할 것:\n"
            "  1. settings.json의 tpl_claiming / tpl_rival 경로\n"
            "  2. assets/templates 폴더에 파일이 실제로 있는지\n"
            "  3. 파일명이 정확한지 (대소문자 포함)\n"
        )

    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise RuntimeError(
            "\n[템플릿 파일 읽기 실패]\n"
            f"- 경로: {path}\n"
            "- 파일이 손상되었거나 OpenCV가 읽을 수 없는 형식일 수 있음\n"
        )

    return img


def match_score(gray_roi: np.ndarray, tpl_gray: np.ndarray) -> float:
    if gray_roi.shape[0] < tpl_gray.shape[0] or gray_roi.shape[1] < tpl_gray.shape[1]:
        return -1.0

    res = cv2.matchTemplate(gray_roi, tpl_gray, cv2.TM_CCOEFF_NORMED)
    _, maxv, _, _ = cv2.minMaxLoc(res)
    return float(maxv)


def yellow_ratio(
    bgr_roi: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
) -> float:
    hsv = cv2.cvtColor(bgr_roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    return float((mask > 0).mean())