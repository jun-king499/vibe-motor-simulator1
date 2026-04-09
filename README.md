# 🏎️ Vibe-Control: Vehicle & Motor PID Simulator
> **누구나 쉽게 이해하고 튜닝하는 차량/모터 제어 시스템 시뮬레이터**

이 프로젝트는 복잡한 제어 공학 이론을 시각적으로 풀어낸 인터랙티브 시뮬레이션 툴입니다. 실제 차량의 주행 환경이나 DC 모터의 물리적 특성을 설정하고, PID 게인 값을 실시간으로 튜닝하며 시스템의 응답을 관찰할 수 있습니다.

![Project Preview]([이곳에_프로그램_실행_스크린샷_혹은_GIF_링크])

## ✨ 주요 기능 (Key Features)

- **실시간 물리 엔진**: 차량(Mass, Friction) 및 모터(Inertia, Damping)의 물리 파라미터를 실시간 반영
- **인터랙티브 PID 튜닝**: Kp, Ki, Kd 게인을 슬라이더로 조절하며 즉각적인 시스템 응답 확인
- **이중 시각화**: 
  - **Graph View**: 시간별 위치/각도 변화를 정밀하게 분석하는 실시간 그래프
  - **Animation View**: 실제 모터 축이 회전하며 목표를 찾아가는 물리 기반 애니메이션
- **원클릭 배포**: 별도의 파이썬 설치 없이 `.exe` 파일만으로 즉시 실행 가능

## 🛠️ 기술 스택 (Tech Stack)

- **Language**: Python 3.12+
- **GUI Framework**: PySide6 (Qt for Python)
- **Visualization**: PyQtGraph, NumPy
- **Packaging**: PyInstaller

## 🚀 시작하기 (Getting Started)

### 1. 실행 파일로 바로 시작하기
코드를 설치할 필요 없이 [Releases](https://github.com/jun-king499/vibe-motor-simulator/releases) 탭에서 최신 버전의 `.exe` 파일을 다운로드하여 실행하세요.

### 2. 소스 코드로 실행하기
```bash
# 리포지토리 클론
git clone [https://github.com/jun-king499/vibe-motor-simulator.git](https://github.com/jun-king499/vibe-motor-simulator.git)

# 가상환경 설정 및 라이브러리 설치
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate
pip install PySide6 pyqtgraph numpy

# 프로그램 실행
python main.py