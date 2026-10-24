import sys
import os
import datetime
import ollama
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, 
                             QHBoxLayout, QVBoxLayout, QTextEdit)
from PyQt5.QtGui import QPixmap, QKeySequence
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal

# ================= 1. 后台请求大模型的线程 =================
class LLMThread(QThread):
    # 定义信号，用于把 AI 的回复传回给主界面
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, messages):
        super().__init__()
        self.messages = messages

    def run(self):
        try:
            # 调用本地 Ollama 的 qwen2 模型
            response = ollama.chat(model='qwen2', messages=self.messages)
            reply = response['message']['content']
            self.response_ready.emit(reply)
        except Exception as e:
            self.error_occurred.emit(f"连接模型出错了，请确认 Ollama 是否运行中。\n错误信息: {e}")


# ================= 2. 宠物头顶的对话气泡 =================
class SpeechBubble(QWidget):
    def __init__(self, parent_pet):
        super().__init__()
        self.pet = parent_pet
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.label = QLabel(self)
        self.label.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 230);
                border: 2px solid #5C9EAD;
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
                color: #333;
            }
        """)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignCenter)

    def show_message(self, text):
        self.label.setText(text)
        # 限制气泡最大宽度
        self.label.setMaximumWidth(250)
        self.label.adjustSize()
        
        # 重新调整气泡窗口大小
        self.resize(self.label.size())
        
        # 计算位置：在宠物头顶居中显示
        pet_x, pet_y = self.pet.x(), self.pet.y()
        pet_w, pet_h = self.pet.width(), self.pet.height()
        
        bubble_x = pet_x + (pet_w - self.width()) // 2
        bubble_y = pet_y - self.height() - 10 # 留出一点间距
        
        self.move(bubble_x, bubble_y)
        self.show()
        self.raise_()
        
        # 气泡显示 8 秒后自动消失
        QTimer.singleShot(8000, self.hide)


# ================= 3. 聊天输入面板 =================
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
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.container = QWidget(self)
        self.container.setStyleSheet("background-color: rgba(240, 248, 255, 220); border-radius: 8px;")
        
        self.h_layout = QHBoxLayout(self.container)
        self.h_layout.setContentsMargins(8, 8, 8, 8)
        self.h_layout.setSpacing(8)

        self.btn_settings = QPushButton("⚙️")
        self.btn_settings.setFixedSize(36, 36)
        self.btn_settings.setStyleSheet("QPushButton { font-size: 20px; background-color: transparent; border: none; } QPushButton:hover { background-color: rgba(200, 200, 200, 100); border-radius: 5px; }")
        self.btn_settings.clicked.connect(self.on_settings_clicked)
        
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("和鲸鱼娘说点什么...")
        self.text_input.setStyleSheet("QTextEdit { background-color: white; border: 1px solid #ccc; border-radius: 5px; font-size: 16px; padding: 4px; }")
        self.text_input.installEventFilter(self)

        self.h_layout.addWidget(self.btn_settings)
        self.h_layout.addWidget(self.text_input)
        self.main_layout.addWidget(self.container)
        
        self.setFixedHeight(60)

    def adjust_width(self, width):
        self.setFixedWidth(width)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.pos().y() >= self.height() - 10:
            self.is_resizing = True
            self.resize_start_pos = event.globalPos()
            self.resize_start_height = self.height()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_resizing:
            delta = event.globalPos() - self.resize_start_pos
            new_height = self.resize_start_height + delta.y()
            if new_height > 60:
                self.setFixedHeight(new_height)
            event.accept()
        else:
            if event.pos().y() >= self.height() - 10:
                self.setCursor(Qt.SizeVerCursor)
            else:
                self.setCursor(Qt.ArrowCursor)

    def mouseReleaseEvent(self, event):
        self.is_resizing = False
        self.setCursor(Qt.ArrowCursor)

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
            self.text_input.clear()
            self.hide()
            
            # 将消息交给宠物主窗口处理
            self.pet.handle_user_message(text)

    def on_settings_clicked(self):
        print("【系统】点击了设置按钮")
        self.hide()
        self.pet.load_image("0.png")


# ================= 4. 主宠物窗口 =================
class WhalePet(QWidget):
    def __init__(self):
        super().__init__()
        self.is_dragging = False
        self.drag_start_pos = None
        self.current_state = "0.png"
        self.just_closed_panel = False
        
        # AI 对话历史记录 (保存在内存中)
        self.chat_history = [
            {"role": "system", "content": "你是一只可爱的鲸鱼娘女仆，名字叫小蓝。你说话语气活泼、带一点海洋气息（比如偶尔提到尾巴、水），每次回答尽量简短（50字以内）。"}
        ]
        self.llm_thread = None

        self.initUI()
        
        self.chat_panel = ChatInputPanel(self)
        self.chat_panel.hide()
        
        self.speech_bubble = SpeechBubble(self)
        self.speech_bubble.hide()

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

    # ================= 核心：处理用户消息并发给 AI =================
    def handle_user_message(self, text):
        # 1. 拼接当前时间
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_msg_with_time = f"[当前时间: {now}] {text}"
        
        # 2. 把用户消息加入历史
        self.chat_history.append({"role": "user", "content": user_msg_with_time})
        
        # 3. 切换思考动作
        self.load_image("think.png")
        
        # 4. 启动后台线程请求 AI
        self.llm_thread = LLMThread(self.chat_history)
        self.llm_thread.response_ready.connect(self.on_ai_reply)
        self.llm_thread.error_occurred.connect(self.on_ai_error)
        self.llm_thread.start()

    def on_ai_reply(self, reply):
        # 恢复站立
        self.load_image("0.png")
        
        # 把 AI 的回复加入历史
        self.chat_history.append({"role": "assistant", "content": reply})
        
        # 显示气泡
        self.speech_bubble.show_message(reply)

    def on_ai_error(self, error_msg):
        self.load_image("0.png")
        self.speech_bubble.show_message(error_msg)

    # ================= 鼠标事件 =================
    def mousePressEvent(self, event):
        if self.chat_panel.isVisible():
            self.chat_panel.hide()
            self.restore_idle()
            self.load_image("0.png")
            self.just_closed_panel = True

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
            if not self.is_dragging and not self.just_closed_panel:
                # 判断当前是不是在思考状态，如果是，不要打断成wave
                if self.current_state != "think.png":
                    self.load_image("wave.png")
                    QTimer.singleShot(1000, self.restore_idle)
            
            self.drag_start_pos = None
            self.is_dragging = False
            self.just_closed_panel = False

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
        self.speech_bubble.close()
        self.close()
        QApplication.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = WhalePet()
    pet.show()
    sys.exit(app.exec_())