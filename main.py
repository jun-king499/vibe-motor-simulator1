import sys
import numpy as np
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                               QWidget, QLabel, QSlider, QGroupBox, QFormLayout, QPushButton)
from PySide6.QtCore import Qt, QTimer
import pyqtgraph as pg

class VibeControlApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vibe-Control: Pro Motor Gain Tuning Simulator")
        self.setGeometry(100, 100, 1200, 750) # 가로를 넓혀서 두 개의 화면을 담습니다.

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- 1. 시각화 영역 (그래프 + 모터 애니메이션) ---
        visual_layout = QHBoxLayout()
        main_layout.addLayout(visual_layout, stretch=3)

        # 1-1. 실시간 응답 그래프 (왼쪽)
        self.plot_widget = pg.PlotWidget(title="시간별 응답 그래프 (Angle vs Time)")
        self.plot_widget.setBackground('#1e1e1e')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.addLegend()
        self.plot_widget.setYRange(-50, 450)
        self.plot_widget.setXRange(0, 10)
        visual_layout.addWidget(self.plot_widget, stretch=2)

        # 현재 시간을 나타내는 노란색 세로선 (커서)
        self.time_line = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('y', width=2))
        self.plot_widget.addItem(self.time_line)

        # 1-2. 모터 회전축 시각화 뷰어 (오른쪽)
        self.motor_view = pg.PlotWidget(title="모터 회전축 (Front View)")
        self.motor_view.setBackground('#2b2b2b')
        self.motor_view.setAspectLocked(True) # 원이 찌그러지지 않게 비율 고정
        self.motor_view.setXRange(-1.5, 1.5)
        self.motor_view.setYRange(-1.5, 1.5)
        self.motor_view.hideAxis('bottom')
        self.motor_view.hideAxis('left')
        visual_layout.addWidget(self.motor_view, stretch=1)

        # 모터 외형(원) 그리기
        theta = np.linspace(0, 2*np.pi, 100)
        self.motor_view.plot(np.cos(theta), np.sin(theta), pen=pg.mkPen('#555555', width=3))
        
        # 목표 각도 선 (빨간 점선)
        self.target_line = self.motor_view.plot([0, 0], [0, 0], pen=pg.mkPen('r', width=2, style=Qt.DashLine))
        # 실제 모터 축 (초록 실선)
        self.shaft_line = self.motor_view.plot([0, 0], [0, 0], pen=pg.mkPen('#00FF00', width=6))

        # --- 2. 제어판 영역 ---
        control_layout = QHBoxLayout()
        main_layout.addLayout(control_layout, stretch=1)

        # [1구역] 입력 신호
        env_group = QGroupBox("1. 목표 입력 (Target Input)")
        env_layout = QFormLayout()
        self.target_slider, self.target_label = self.create_slider("목표 각도", 0, 360, 90, 1, "deg")
        env_layout.addRow(self.target_label, self.target_slider)
        
        # 다시 재생하기 버튼 추가 (바이브 포인트!)
        self.btn_replay = QPushButton("애니메이션 다시 재생 🔄")
        self.btn_replay.setStyleSheet("background-color: #007acc; color: white; padding: 5px; font-weight: bold;")
        self.btn_replay.clicked.connect(self.calculate_simulation)
        env_layout.addRow(self.btn_replay)
        
        env_group.setLayout(env_layout)
        control_layout.addWidget(env_group)

        # [2구역] 모터 제원
        motor_group = QGroupBox("2. 모터 제원 (Plant)")
        motor_layout = QFormLayout()
        self.inertia_slider, self.inertia_label = self.create_slider("회전 관성 (J)", 1, 100, 10, 100, "kg·m²")
        self.damping_slider, self.damping_label = self.create_slider("점성 마찰 (b)", 0, 50, 5, 10, "N·m·s")
        motor_layout.addRow(self.inertia_label, self.inertia_slider)
        motor_layout.addRow(self.damping_label, self.damping_slider)
        motor_group.setLayout(motor_layout)
        control_layout.addWidget(motor_group)

        # [3구역] 제어기 설정
        pid_group = QGroupBox("3. PID 게인 튜닝 (Controller)")
        pid_layout = QFormLayout()
        self.p_slider, self.p_label = self.create_slider("Kp (비례)", 0, 500, 150, 10, "")
        self.i_slider, self.i_label = self.create_slider("Ki (적분)", 0, 100, 5, 10, "")
        self.d_slider, self.d_label = self.create_slider("Kd (미분)", 0, 200, 30, 10, "")
        pid_layout.addRow(self.p_label, self.p_slider)
        pid_layout.addRow(self.i_label, self.i_slider)
        pid_layout.addRow(self.d_label, self.d_slider)
        pid_group.setLayout(pid_layout)
        control_layout.addWidget(pid_group)

        # --- 애니메이션을 위한 변수 및 타이머 설정 ---
        self.t_data = []
        self.angle_data = []
        self.target_data = []
        self.current_frame = 0
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        
        # 앱 시작 시 최초 계산 및 재생
        self.calculate_simulation()

    def create_slider(self, name, min_val, max_val, default_val, scale=1, unit=""):
        label = QLabel(f"{name}: {default_val/scale:.2f} {unit}")
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        
        slider.valueChanged.connect(lambda val, l=label, n=name, s=scale, u=unit: l.setText(f"{n}: {val/s:.2f} {u}"))
        # 슬라이더 변경 시 시뮬레이션 재계산
        slider.valueChanged.connect(self.calculate_simulation)
        return slider, label

    def calculate_simulation(self):
        """설정값을 바탕으로 전체 물리 연산을 0.05초 단위로 한 번에 미리 계산합니다."""
        target_angle = float(self.target_slider.value())
        inertia_J = max(self.inertia_slider.value() / 100.0, 0.01)
        damping_b = self.damping_slider.value() / 10.0
        kp = self.p_slider.value() / 10.0
        ki = self.i_slider.value() / 10.0
        kd = self.d_slider.value() / 10.0

        dt = 0.05
        time_steps = 200 # 10초 분량
        
        current_angle = 0.0
        angular_velocity = 0.0
        integral = 0.0
        prev_error = target_angle - current_angle

        self.t_data = []
        self.angle_data = []
        self.target_data = []

        for i in range(time_steps):
            t = i * dt
            
            error = target_angle - current_angle
            integral += error * dt
            derivative = (error - prev_error) / dt
            
            torque = (kp * error) + (ki * integral) + (kd * derivative)
            angular_accel = (torque - damping_b * angular_velocity) / inertia_J
            
            angular_velocity += angular_accel * dt
            current_angle += angular_velocity * dt
            prev_error = error

            self.t_data.append(t)
            self.angle_data.append(current_angle)
            self.target_data.append(target_angle)

        # 그래프 바탕 그리기 (애니메이션과 무관하게 한 번에 그림)
        self.plot_widget.clear()
        self.plot_widget.plot(self.t_data, self.target_data, pen=pg.mkPen('r', width=2, style=Qt.DashLine), name="목표 각도")
        self.plot_widget.plot(self.t_data, self.angle_data, pen=pg.mkPen('#44aa44', width=2), name="예상 궤적 (배경)")
        self.plot_widget.addItem(self.time_line) # 커서 다시 추가
        
        # 오른쪽 모터 뷰어의 목표선 그리기 (고정)
        rad_target = np.radians(target_angle)
        self.target_line.setData([0, np.cos(rad_target)], [0, np.sin(rad_target)])

        # 애니메이션 초기화 및 시작
        self.current_frame = 0
        self.timer.start(50) # 50ms 마다 화면 업데이트 (실제 시간과 거의 동일)

    def update_animation(self):
        """타이머에 맞춰 그래프의 커서와 모터 축을 움직입니다."""
        if self.current_frame >= len(self.t_data):
            self.timer.stop() # 끝까지 재생되면 멈춤
            return
            
        current_t = self.t_data[self.current_frame]
        current_a = self.angle_data[self.current_frame]
        
        # 1. 왼쪽 그래프: 시간 커서 이동
        self.time_line.setPos(current_t)
        
        # 2. 오른쪽 뷰어: 모터 축 회전
        rad_current = np.radians(current_a)
        self.shaft_line.setData([0, np.cos(rad_current)], [0, np.sin(rad_current)])
        
        self.current_frame += 1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # UI 스타일 살짝 다듬기
    app.setStyleSheet("""
        QGroupBox { font-weight: bold; font-size: 14px; border: 1px solid gray; border-radius: 5px; margin-top: 10px; }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }
    """)
    window = VibeControlApp()
    window.show()
    sys.exit(app.exec())