import time

import cv2
import numpy as np

from config import BotConfig, State
from image_utils import (
    crop,
    ensure_dir,
    load_gray_image_or_die,
    match_score,
    to_gray,
    yellow_ratio,
)
from sender import SwitchSender


class ShinyMacroBot:
    def __init__(self, config: BotConfig):
        self.cfg = config

        ensure_dir(self.cfg.debug_dir)
        ensure_dir(self.cfg.manual_capture_dir)
        ensure_dir(self.cfg.full_dir)

        self.yellow_lower = np.array(self.cfg.yellow_lower)
        self.yellow_upper = np.array(self.cfg.yellow_upper)

        self.sender = SwitchSender(
            host=self.cfg.esp_host,
            port=self.cfg.esp_port,
            tap_press=self.cfg.tap_press,
        )

        self.cap = cv2.VideoCapture(self.cfg.cap_index)
        if not self.cap.isOpened():
            self.sender.close()
            raise RuntimeError(
                "\n[캡처 장치 열기 실패]\n"
                f"- CAP_INDEX: {self.cfg.cap_index}\n"
                "- 확인할 것:\n"
                "  1. 캡처보드 또는 OBS Virtual Camera가 켜져 있는지\n"
                "  2. 현재 설정한 cap_index가 맞는지\n"
                "  3. 다른 프로그램이 장치를 점유 중인지\n"
                "  4. OBS를 쓰는 경우 'Start Virtual Camera'를 눌렀는지\n"
            )

        self.tpl_claiming = load_gray_image_or_die(self.cfg.tpl_claiming)
        self.tpl_rival = load_gray_image_or_die(self.cfg.tpl_rival)

        self.state = State.SPAM_A
        self.last_spam = time.time()
        self.last_check = 0.0
        self.not_shiny_count = 0

        self.rival_seen = 0
        self.last_rival_hit = 0.0

        self.seq_step = 0
        self.next_action_time = 0.0
        self.last_yellow_ratio = 0.0

        cv2.namedWindow(self.cfg.main_window, cv2.WINDOW_NORMAL)

    def reset_to_spam_a(self) -> None:
        self.state = State.SPAM_A
        self.last_spam = time.time()
        self.rival_seen = 0
        self.last_rival_hit = 0.0
        self.seq_step = 0
        self.next_action_time = 0.0

    def manual_reset(self) -> None:
        print("manual reset ABXY")
        self.sender.combo_tap("ABXY")
        self.reset_to_spam_a()

    def save_manual_shiny_roi(self, frame) -> None:
        shiny_live = crop(frame, self.cfg.roi_shiny)
        if shiny_live.size == 0:
            print("ROI_SHINY empty - cannot save")
            return

        ts = int(time.time() * 1000)
        debug_path = self.cfg.manual_capture_dir / f"manual_{ts}.png"
        ok = cv2.imwrite(str(debug_path), shiny_live)
        print("manual ROI saved:", debug_path, "ok=", ok, "shape=", shiny_live.shape)

    def read_frame(self):
        ok, frame = self.cap.read()
        if not ok:
            return None
        return frame

    def get_scores(self, frame) -> tuple[float, float]:
        g_claim = to_gray(crop(frame, self.cfg.roi_claiming))
        g_rival = to_gray(crop(frame, self.cfg.roi_rival))

        sc_claim = match_score(g_claim, self.tpl_claiming)
        sc_rival = match_score(g_rival, self.tpl_rival)
        return sc_claim, sc_rival

    def handle_spam_a(self, now: float, claiming_detected: bool) -> None:
        if now - self.last_spam >= self.cfg.spam_period:
            self.sender.tap("A")
            self.last_spam = now

        if claiming_detected:
            self.sender.tap("A")
            self.state = State.SPAM_B
            self.last_spam = time.time()
            time.sleep(0.15)
            self.rival_seen = 0
            self.last_rival_hit = 0.0

    def handle_spam_b(self, now: float, rival_detected: bool, sc_rival: float) -> None:
        if now - self.last_spam >= self.cfg.spam_period:
            self.sender.tap("B")
            self.last_spam = now

        if rival_detected and (now - self.last_rival_hit >= self.cfg.rival_hit_cooldown):
            self.rival_seen += 1
            self.last_rival_hit = now
            print(f"rival_claim seen {self.rival_seen}/2 (score={sc_rival:.3f})")

            if self.rival_seen >= 2:
                self.state = State.RIVAL_SEQ
                self.seq_step = 0
                self.next_action_time = time.time() + 2.0

    def handle_rival_seq(self, now: float) -> None:
        if now < self.next_action_time:
            return

        if self.seq_step == 0:
            self.sender.tap("B")
            self.next_action_time = now + 1.0
        elif self.seq_step == 1:
            self.sender.tap("X")
            self.next_action_time = now + 1.0
        elif self.seq_step == 2:
            self.sender.tap("A")
            self.next_action_time = now + 1.0
        elif self.seq_step == 3:
            self.sender.tap("A")
            self.next_action_time = now + 1.0
        elif self.seq_step == 4:
            self.sender.tap("A")
            self.next_action_time = now + self.cfg.after_seq_wait
        elif self.seq_step == 5:
            time.sleep(2.0)
            self.state = State.CHECK_SHINY
            self.last_check = 0.0
            return

        self.seq_step += 1

    def handle_check_shiny(self, now: float, frame) -> None:
        if now - self.last_check < self.cfg.check_cooldown:
            return

        self.last_check = now

        shiny_roi_bgr = crop(frame, self.cfg.roi_shiny)
        if shiny_roi_bgr.size == 0:
            print("ROI_SHINY empty - check ROI coords")
            return

        if float(shiny_roi_bgr.mean()) < self.cfg.black_mean_th:
            return

        ratio = yellow_ratio(
            shiny_roi_bgr,
            self.yellow_lower,
            self.yellow_upper,
        )
        self.last_yellow_ratio = ratio
        print(f"yellow_ratio={ratio:.6f} (TH={self.cfg.yellow_th})")

        if ratio >= self.cfg.yellow_th:
            print("SHINY DETECTED (yellow_ratio) -> SAVE + WAIT")
            shiny_path = self.cfg.full_dir / f"SHINY_{int(time.time())}.png"
            ok = cv2.imwrite(str(shiny_path), frame)
            print("SHINY SAVED:", shiny_path, "ok=", ok)
            print("WAITING... press 'r' to reset")
            self.state = State.SHINY_WAIT
            return

        self.not_shiny_count += 1
        print(f"not shiny ({self.not_shiny_count}) -> ABXY")

        full_path = self.cfg.full_dir / f"{self.not_shiny_count:06d}.png"
        ok = cv2.imwrite(str(full_path), frame)
        print("saved full:", full_path, "ok=", ok)

        time.sleep(1.00)
        self.sender.combo_tap("ABXY")
        time.sleep(0.25)
        self.state = State.SPAM_A
        self.last_spam = time.time()

    def draw_overlay(
        self,
        frame,
        state: State,
        sc_claim: float,
        sc_rival: float,
    ) -> None:
        disp = frame.copy()

        cv2.rectangle(disp, self.cfg.roi_claiming[:2], self.cfg.roi_claiming[2:], (0, 255, 0), 2)
        cv2.rectangle(disp, self.cfg.roi_rival[:2], self.cfg.roi_rival[2:], (0, 255, 0), 2)
        cv2.rectangle(disp, self.cfg.roi_shiny[:2], self.cfg.roi_shiny[2:], (0, 255, 0), 2)

        cv2.putText(
            disp,
            f"state={state.value}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
        cv2.putText(
            disp,
            f"claim={sc_claim:.3f} rival={sc_rival:.3f} rival_seen={self.rival_seen}/2",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0),
            2,
        )
        cv2.putText(
            disp,
            f"count={self.not_shiny_count}",
            (20, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0),
            2,
        )
        cv2.putText(
            disp,
            f"yellow={self.last_yellow_ratio:.6f}",
            (20, 160),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0),
            2,
        )

        cv2.imshow(self.cfg.main_window, disp)

    def run(self) -> None:
        try:
            while True:
                frame = self.read_frame()
                if frame is None:
                    continue

                now = time.time()
                key = cv2.waitKey(1) & 0xFF

                if key == ord("q"):
                    print("quit")
                    break
                elif key == ord("r"):
                    self.manual_reset()

                if key == ord("s"):
                    self.save_manual_shiny_roi(frame)

                sc_claim, sc_rival = self.get_scores(frame)
                claiming_detected = sc_claim >= self.cfg.th_claiming
                rival_detected = sc_rival >= self.cfg.th_rival

                if self.state == State.SPAM_A:
                    self.handle_spam_a(now, claiming_detected)
                elif self.state == State.SPAM_B:
                    self.handle_spam_b(now, rival_detected, sc_rival)
                elif self.state == State.RIVAL_SEQ:
                    self.handle_rival_seq(now)
                elif self.state == State.CHECK_SHINY:
                    self.handle_check_shiny(now, frame)
                elif self.state == State.SHINY_WAIT:
                    pass

                self.draw_overlay(frame, self.state, sc_claim, sc_rival)

        finally:
            self.cap.release()
            cv2.destroyAllWindows()
            self.sender.close()