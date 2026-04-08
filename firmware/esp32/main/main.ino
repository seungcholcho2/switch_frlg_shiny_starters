#include <switch_ESP32.h>
#include <WiFi.h>

WiFiServer server(9999);
WiFiClient client;
NSGamepad Gamepad;

// AP 정보
const char* AP_SSID = "ESP32_AP";
const char* AP_PASS = "12345678"; // 8자 이상

static const uint32_t SPAM_MS = 3000;
static const uint32_t SPAM_PERIOD = 40;
static const uint32_t SPAM_PRESS_MS = 10;

uint32_t bootMs = 0;
uint32_t lastSpamMs = 0;
bool spamPressing = false;
uint32_t spamPressStartMs = 0;

void handleCmd(char c) {
  if (c == 'A') Gamepad.press(NSButton_A);
  if (c == 'a') Gamepad.release(NSButton_A);

  if (c == 'B') Gamepad.press(NSButton_B);
  if (c == 'b') Gamepad.release(NSButton_B);

  if (c == 'X') Gamepad.press(NSButton_X);
  if (c == 'x') Gamepad.release(NSButton_X);

  if (c == 'Y') Gamepad.press(NSButton_Y);
  if (c == 'y') Gamepad.release(NSButton_Y);

  if (c == 'R') Gamepad.press(NSButton_RightTrigger);
  if (c == 'r') Gamepad.release(NSButton_RightTrigger);
}

static void spamAFor3s() {
  uint32_t now = millis();
  if (now - bootMs > SPAM_MS) {
    if (spamPressing) {
      Gamepad.release(NSButton_A);
      spamPressing = false;
    }
    return;
  }

  if (!spamPressing && (now - lastSpamMs >= SPAM_PERIOD)) {
    Gamepad.press(NSButton_A);
    spamPressing = true;
    spamPressStartMs = now;
    lastSpamMs = now;
  }

  if (spamPressing && (now - spamPressStartMs >= SPAM_PRESS_MS)) {
    Gamepad.release(NSButton_A);
    spamPressing = false;
  }
}

void setup() {
  Serial.begin(115200);
  delay(300);

  // 1) AP 모드로 전환
  WiFi.mode(WIFI_AP);
  bool ok = WiFi.softAP(AP_SSID, AP_PASS);
  Serial.printf("AP start: %s\n", ok ? "OK" : "FAIL");
  Serial.print("AP SSID: "); Serial.println(AP_SSID);
  Serial.print("AP IP  : "); Serial.println(WiFi.softAPIP()); // 보통 192.168.4.1

  // 2) TCP 서버 시작
  server.begin();
  Serial.println("TCP server started on port 9999");

  // 3) 게임패드 시작
  Gamepad.begin();
  USB.begin();

  bootMs = millis();
  lastSpamMs = bootMs;

  Serial.println("READY");
}

void loop() {
  spamAFor3s();

  // 새 연결 받기
  if (!client || !client.connected()) {
    client = server.available();
  }

  // 들어온 데이터 처리
  if (client && client.connected()) {
    while (client.available()) {
      char c = client.read();
      handleCmd(c);
    }
  }

  Gamepad.loop();
}