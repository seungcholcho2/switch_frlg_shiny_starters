# 🟣 Pokémon FR/LG Shiny Hunting Macro (ESP32 + OpenCV)

Nintendo Switch에서 포켓몬 FR/LG 스타팅 이로치 작업을 자동화하는 매크로 환경 구축 가이드임.

---

## 📦 1. Requirements

### 필수 장비
- Nintendo Switch (1 / 2 모두 가능)
- Pokémon FireRed / LeafGreen (영문판 필수)
- Wi-Fi 가능한 PC 또는 노트북
- ESP32-S3 (USB 2포트 권장)
- 캡쳐보드
- USB 케이블
  - A to C (Switch ↔ ESP32)
  - C to C 또는 A to C (PC ↔ ESP32)

### 필수 소프트웨어
- Python 3.10 이상
- OBS Studio
- Arduino IDE 2

---

## 🐍 2. Python 설치 및 터미널 사용

### 2-1. Python 설치
- https://www.python.org/downloads/
- Python 3.10 이상 설치

⚠️ 설치 시 반드시 체크:
- `Add Python to PATH`

---

### 2-2. 설치 확인

터미널 실행:

- Windows: `cmd`
- Mac: `cmd + space → Terminal`

```bash
python --version
# 또는
python3 --version
```

---

## 📁 3. 프로젝트 다운로드 및 설정

### 3-1. 폴더 생성
- 바탕화면에 영문 이름 폴더 생성 (예: `shiny_macro`)

---

### 3-2. 레포 다운로드
1. 본 프로젝트 ZIP 다운로드 후 폴더에 압축 해제
2. 아래 라이브러리 다운로드 (압축 풀지 않음)

- https://github.com/esp32beans/switch_ESP32

---

### 3-3. 터미널 이동

```bash
cd Desktop/shiny_macro
```

---

### 3-4. 가상환경 생성 및 실행

```bash
# 가상환경 생성
python3 -m venv venv

# 실행 (Mac)
source venv/bin/activate

# 실행 (Windows)
venv\Scripts\activate
```

---

### 3-5. 라이브러리 설치

```bash
pip install -r requirements.txt
```

---

## 🎥 4. OBS 설치 및 설정

### 4-1. OBS 설치
- https://obsproject.com/

---

### 4-2. 캡쳐보드 연결

1. OBS 실행
2. Sources → `+` → **Video Capture Device**
3. 캡쳐보드 선택
4. Switch 화면 정상 출력 확인

---

## ⚙️ 5. ESP32 설정

### 5-1. Arduino IDE 설치
- Arduino IDE 2 설치

---

### 5-2. ESP32 보드 추가

- Arduino IDE → Boards Manager
- `esp32` 검색 후 설치

---

### 5-3. 라이브러리 추가

Sketch → Include Library → Add .ZIP Library  
→ switch_ESP32 ZIP 선택

---

### 5-4. 보드 및 포트 설정

Tools → Board → ESP32S3 Dev Module  
Tools → Port → ESP32 연결 포트 선택

---

### 5-5. 업로드

- 코드 업로드
- 완료 후 Wi-Fi 목록에서 `ESP32_AP` 확인

---

## 🚀 6. 프로그램 실행

### 6-1. 사전 준비

1. ESP32 → Switch 연결
2. OBS 실행
3. **가상 카메라 시작**

---

### 6-2. 게임 상태 준비

1. 독 없이 실행
2. 스타팅 선택 직전까지 진행 후 저장
3. `A + B + X + Y` → 초기화
4. Switch를 독에 연결

---

### 6-3. PC 연결

- Wi-Fi → `ESP32_AP` 연결

---

### 6-4. 실행

```bash
python3 main.py
```

---

### 6-5. 화면 확인

- 새 창에 Switch 화면 출력 확인

❗ 안 나오면:

`Setting.json` 수정:

```json
"cap_index": 0
```

👉 0 - 4 사이 값으로 변경하며 테스트

---

### 6-6. 종료 방법

- 창 선택 후 `q` 입력  
- 안되면 한/영키 변경 후 다시 시도

---

### 6-7. 반복 실행

1. Switch 독 분리  
2. `A + B + X + Y`  
3. 다시 독 연결  
4. 프로그램 재실행  

---

## 🛠 문제 해결 (Troubleshooting)

### 📺 화면 안 나올 때
- OBS 실행 확인  
- 가상 카메라 활성화 확인  
- Zoom/Discord 등 캡쳐보드 점유 프로그램 종료  
- `cap_index` 변경  

---

### 🔌 ESP32 인식 안 될 때
- 포트 다시 선택  
- 케이블 교체  
- 드라이버 확인  

---

### 🐍 Python 실행 안 될 때
- PATH 설정 확인  
- `python` vs `python3` 둘 다 시도  

---

## 📌 참고

- cap_index 일반 기준:
  - 0: 웹캠  
  - 1 - 3: 캡쳐보드  

---

## 🎯 목표

- 완전 자동 이로치 작업  
- 사람 개입 없이 반복 수행  

---

## ⚠️ 주의

- 영문판만 정상 동작  
- 캡쳐보드 환경 따라 index 다름  
- ESP32 모델 호환 확인 필요  
