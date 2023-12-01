import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, QFileDialog
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt
from PIL import Image

class ADBApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

        # 타이머를 사용하여 주기적으로 기기 연결 상태를 확인
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_device_connection)
        self.timer.start(500)  # 0.5초 간격으로 타이머 실행

    def init_ui(self):
        self.setWindowTitle('ADB 스크린샷 슈터 v1.0.0')
        self.setFixedSize(1280, 900)  # 윈도우 최대 크기 고정

        self.device_status_label = QLabel('ADB 연결상태 : Not Connected')
        self.screenshot_label = QLabel('스크린샷 위치')
        self.screenshot_button = QPushButton('스크린샷 찍기')
        self.save_button = QPushButton('다른이름으로 저장')
        self.restart_adb_button = QPushButton('ADB 재시작')

        layout = QVBoxLayout()
        layout.addWidget(self.device_status_label)
        layout.addWidget(self.screenshot_label)
        layout.addWidget(self.screenshot_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.restart_adb_button)

        self.screenshot_button.clicked.connect(self.take_screenshot)
        self.save_button.clicked.connect(self.save_screenshot)
        self.restart_adb_button.clicked.connect(self.restart_adb)

        self.setLayout(layout)

    def check_device_connection(self):
        try:
            adb_devices_output = subprocess.check_output(['adb', 'devices']).decode('utf-8')
            if 'device' in adb_devices_output:
                self.device_status_label.setText('ADB 상태: Connected')
                self.restart_adb_button.setEnabled(False)  # 연결되어 있으면 ADB 재시작 버튼 비활성화
            else:
                self.device_status_label.setText('ADB 상태: Not Connected')
                self.restart_adb_button.setEnabled(True)  # 연결되어 있지 않으면 ADB 재시작 버튼 활성화
        except subprocess.CalledProcessError:
            self.show_message('Error', 'Error while checking ADB devices.')

    def take_screenshot(self):
        # ADB 체크
        try:
            subprocess.run(['adb', '--version'], check=True)
        except subprocess.CalledProcessError:
            self.show_message('Error', 'ADB 설치되어 있지 않거나, 환경변수 지정이 되어있지 않습니다.')
            return

        # 디바이스 연결 체크
        try:
            adb_devices_output = subprocess.check_output(['adb', 'devices']).decode('utf-8')
            if 'device' not in adb_devices_output:
                self.show_message('Error', '연결된 안드로이드 기기가 없습니다.')
                return
        except subprocess.CalledProcessError:
            self.show_message('Error', 'Error while checking ADB devices.')
            return

        # ADB 이용해 스크린샷 찍기
        try:
            subprocess.run(['adb', 'shell', 'screencap', '/sdcard/screenshot.png'], check=True)
            subprocess.run(['adb', 'pull', '/sdcard/screenshot.png', 'screenshot.png'], check=True)
        except subprocess.CalledProcessError:
            self.show_message('Error', 'Error while taking or pulling the screenshot.')
            return

        # 스크린샷을 앱에 출력
        screenshot_path = 'screenshot.png'
        pixmap = QPixmap(screenshot_path)
        pixmap = pixmap.scaledToHeight(750, Qt.SmoothTransformation)

        self.screenshot_label.setPixmap(pixmap)
        self.screenshot_label.setAlignment(Qt.AlignCenter)  # 이미지를 가운데 정렬


        # 상태 업데이트
        self.device_status_label.setText('ADB 상태: Connected')

    def save_screenshot(self):
        # Open file dialog to select save location
        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("Images (*.png *.jpg)")
        if file_dialog.exec_() == QFileDialog.Accepted:
            save_path = file_dialog.selectedFiles()[0]
        else:
            return

        # 스크린샷을 지정된 위치에 저장
        screenshot_path = 'screenshot.png'
        try:
            Image.open(screenshot_path).save(save_path)
            self.show_message('Success', f'Screenshot saved to {save_path}')
        except Exception as e:
            self.show_message('Error', f'Error saving screenshot: {str(e)}')

    def restart_adb(self):
        try:
            subprocess.run(['adb', 'kill-server'], check=True)
            subprocess.run(['adb', 'start-server'], check=True)
            self.show_message('Success', 'ADB restarted successfully.')
        except subprocess.CalledProcessError:
            self.show_message('Error', 'Error while restarting ADB.')

    def show_message(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    adb_app = ADBApp()
    adb_app.show()
    sys.exit(app.exec_())
