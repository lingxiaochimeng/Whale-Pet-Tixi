import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer

class WhalePet(QWidget):
    def __init__(self):
        super().__init__()
        # 状态变量
        self.is_dragging = False       # 是否正在拖拽
        self.drag_start_pos = None     # 鼠标按下的起始位置
        self.current_state = "0.png"   # 当前动作图

        self.initUI()

    def initUI(self):
        # 1. 窗口设置：无边框、置顶、不显示在任务栏
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        # 2. 透明背景
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 3. 使用 QLabel 来显示图片
        self.label = QLabel(self)
        self.load_image("0.png")
        
        # 4. 初始位置（屏幕右下角附近）
        self.move(1000, 600)

    def load_image(self, image_name):
        """加载图片并调整窗口大小"""
        path = os.path.join(os.path.dirname(__file__), "assets", image_name)
        pixmap = QPixmap(path)
        
        # 如果你发现图片太大，可以在这里缩放，比如:
        # pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        self.label.setPixmap(pixmap)
        self.resize(pixmap.size())
        self.current_state = image_name

    # ================= 鼠标事件 =================

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 记录按下时的全局坐标，并重置拖拽标志
            self.drag_start_pos = event.globalPos()
            self.is_dragging = False
        elif event.button() == Qt.RightButton:
            # 右键点击：切换为等待状态
            self.load_image("wait.png")
            # 后面我们在这里弹出输入框

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_start_pos:
            # 计算鼠标移动距离
            delta = event.globalPos() - self.drag_start_pos
            
            # 如果移动距离超过 5 像素，说明用户是在拖拽，而不是单击
            if delta.manhattanLength() > 5:
                self.is_dragging = True
            
            if self.is_dragging:
                self.move(self.pos() + delta)
                self.drag_start_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.is_dragging:
                # 如果没发生拖拽，这就是一次“单击”
                self.load_image("wave.png")
                # 1秒后恢复站立
                QTimer.singleShot(1000, self.restore_idle)
            
            self.drag_start_pos = None
            self.is_dragging = False

    def restore_idle(self):
        """如果当前不是等待或思考状态，就恢复到站立"""
        if self.current_state in ["wave.png", "walk1.png", "walk2.png"]:
            self.load_image("0.png")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = WhalePet()
    pet.show()
    sys.exit(app.exec_())