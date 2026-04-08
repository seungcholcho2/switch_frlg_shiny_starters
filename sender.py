import socket
import time


class SwitchSender:
    def __init__(self, host: str, port: int, tap_press: float):
        self.tap_press = tap_press
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.sock.connect((host, port))
            self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except OSError as e:
            self.sock.close()
            raise RuntimeError(
                "\n[ESP 연결 실패]\n"
                f"- host: {host}\n"
                f"- port: {port}\n"
                "- 확인할 것:\n"
                "  1. ESP32 전원이 켜져 있는지\n"
                "  2. ESP32 서버가 실행 중인지\n"
                "  3. 현재 PC가 ESP32 AP/Wi-Fi에 연결되어 있는지\n"
                "  4. IP/포트가 settings.json과 일치하는지\n"
            ) from e

    def send(self, ch: str) -> None:
        try:
            self.sock.sendall(ch.encode("ascii"))
        except OSError as e:
            raise RuntimeError(
                "\n[ESP 명령 전송 실패]\n"
                f"- 전송하려던 키: {ch}\n"
                "- 연결이 끊겼거나 ESP32 측에서 소켓이 종료되었을 수 있음\n"
            ) from e

    def down(self, key: str) -> None:
        self.send(key.upper())

    def up(self, key: str) -> None:
        self.send(key.lower())

    def tap(self, key: str, press_s: float | None = None) -> None:
        press_time = self.tap_press if press_s is None else press_s
        self.down(key)
        time.sleep(press_time)
        self.up(key)
        time.sleep(0.02)

    def combo_tap(self, keys: str, press_s: float | None = None) -> None:
        press_time = self.tap_press if press_s is None else press_s
        for key in keys:
            self.down(key)
        time.sleep(press_time)
        for key in keys:
            self.up(key)
        time.sleep(0.03)

    def close(self) -> None:
        self.sock.close()