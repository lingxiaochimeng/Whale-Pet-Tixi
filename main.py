import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, 
                             QHBoxLayout, QVBoxLayout, QTextEdit)
from PyQt5.QtGui import QPixmap, QKeySequence
from PyQt5.QtCore import Qt, QTimer

class ChatInputPanel(QWidget):
    def __init__(self, parent_pet):
        super().__init__()
        self.pet = parent_pet
        self.is_resizing = False
        self.resize_start_pos = None
        self.resize_start_height = 0
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.initUI()

    def initUI(self):
        # 主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 容器（淡蓝色背景）
        self.container = QWidget(self)
        self.container.setStyleSheet("background-color: rgba(240, 248, 255, 220); border-radius: 8px;")
        
        # 容器内水平布局
        self.h_layout = QHBoxLayout(self.container)
        self.h_layout.setContentsMargins(8, 8, 8, 8)
        self.h_layout.setSpacing(8)

        # 设置按钮（换成齿轮图标）
        self.btn_settings = QPushButton("⚙️")
        self.btn_settings.setFixedSize(36, 36)
        self.btn_settings.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(200, 200, 200, 100);
                border-radius: 5px;
            }
        """)
        self.btn_settings.clicked.connect(self.on_settings_clicked)
        
        # 多行输入框（去掉了固定高度，字号变大）
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("和鲸鱼娘说点什么...")
        self.text_input.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 16px;
                padding: 4px;
            }
        """)
        self.text_input.installEventFilter(self)

        self.h_layout.addWidget(self.btn_settings)
        self.h_layout.addWidget(self.text_input)
        
        self.main_layout.addWidget(self.container)
        
        # 默认高度
        self.setFixedHeight(60)

    def adjust_width(self, width):
        """宽度严格跟随宠物，输入框自动适配"""
        self.setFixedWidth(width)

    # ================= 面板边缘拖拽缩放（仅支持往下拉伸高度） =================
    def mousePressEvent(self, event):
        # 判断鼠标是否在底部边缘 10 像素内
        if event.button() == Qt.LeftButton and event.pos().y() >= self.height() - 10:
            self.is_resizing = True
            self.resize_start_pos = event.globalPos()
            self.resize_start_height = self.height()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_resizing:
            delta = event.globalPos() - self.resize_start_pos
            new_height = self.resize_start_height + delta.y()
            if new_height > 60: # 限制最小高度
                self.setFixedHeight(new_height)
            event.accept()
        else:
            # 改变鼠标指针样式提示可以拖拽
            if event.pos().y() >= self.height() - 10:
                self.setCursor(Qt.SizeVerCursor)
            else:
                self.setCursor(Qt.ArrowCursor)

    def mouseReleaseEvent(self, event):
        self.is_resizing = False
        self.setCursor(Qt.ArrowCursor)

    # ================= 输入框逻辑 =================
    def eventFilter(self, obj, event):
        if obj == self.text_input and event.type() == event.KeyPress:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                if event.modifiers() == Qt.ShiftModifier:
                    return False
                else:
                    self.send_message()
                    return True
        return super().eventFilter(obj, event)

    def send_message(self):
        text = self.text_input.toPlainText().strip()
        if text:
            print(f"【用户发送】: {text}")
            self.text_input.clear()
            self.hide()
            self.pet.load_image("0.png") # 发送后恢复站立

    def on_settings_clicked(self):
        print("【系统】点击了设置按钮，下一步实现独立设置窗口")
        self.hide()
        self.pet.load_image("0.png")


class WhalePet(QWidget):
    def __init__(self):
        super().__init__()
        self.is_dragging = False
        self.drag_start_pos = None
        self.current_state = "0.png"
        self.just_closed_panel = False # 修复点击面板消失后触发动画的Bug

        self.initUI()
        
        self.chat_panel = ChatInputPanel(self)
        self.chat_panel.hide()

        from PyQt5.QtWidgets import QShortcut
        self.esc_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.esc_shortcut.activated.connect(self.close_program)

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.label = QLabel(self)
        self.load_image("0.png")
        self.move(1000, 600)

    def load_image(self, image_name):
        path = os.path.join(os.path.dirname(__file__), "assets", image_name)
        pixmap = QPixmap(path)
        self.label.setPixmap(pixmap)
        self.resize(pixmap.size())
        self.current_state = image_name

    def mousePressEvent(self, event):
        if self.chat_panel.isVisible():
            self.chat_panel.hide()
            self.restore_idle()
            self.load_image("0.png")
            self.just_closed_panel = True # 标记刚刚关闭了面板

        if event.button() == Qt.LeftButton:
            self.drag_start_pos = event.globalPos()
            self.is_dragging = False
        elif event.button() == Qt.RightButton:
            self.load_image("wait.png")
            self.show_chat_panel()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_start_pos:
            delta = event.globalPos() - self.drag_start_pos
            if delta.manhattanLength() > 5:
                self.is_dragging = True
            if self.is_dragging:
                self.move(self.pos() + delta)
                self.drag_start_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 如果既没拖拽，也没刚刚关闭面板，才触发wave动画
            if not self.is_dragging and not self.just_closed_panel:
                self.load_image("wave.png")
                QTimer.singleShot(1000, self.restore_idle)
            
            self.drag_start_pos = None
            self.is_dragging = False
            self.just_closed_panel = False # 重置标记

    def restore_idle(self):
        if self.current_state in ["wave.png", "walk1.png", "walk2.png", "wait.png"]:
            self.load_image("0.png")

    def show_chat_panel(self):
        self.chat_panel.adjust_width(self.width())
        panel_x = self.x()
        panel_y = self.y() + self.height() + 5
        self.chat_panel.move(panel_x, panel_y)
        self.chat_panel.show()
        self.chat_panel.raise_()
        self.chat_panel.text_input.setFocus()

    def close_program(self):
        self.chat_panel.close()
        self.close()
        QApplication.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = WhalePet()
    pet.show()
    sys.exit(app.exec_())