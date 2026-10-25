# settings_dialog.py
import ollama
from PyQt5.QtWidgets import (QDialog, QTabWidget, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QComboBox, QSlider, 
                             QTextEdit, QPushButton, QListWidget, QMessageBox,
                             QListWidgetItem)
from PyQt5.QtCore import Qt

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_pet = parent
        self.config = parent.config  # 把 parent_pet 改成 parent
        
        self.setWindowTitle("鲸鱼娘桌宠 - 设置")
        self.resize(450, 400)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        
        self.tab_basic = QWidget()
        self.tab_ai = QWidget()
        self.tab_history = QWidget()
        self.tab_about = QWidget()
        
        self.tabs.addTab(self.tab_basic, "基础设置")
        self.tabs.addTab(self.tab_ai, "AI 设定")
        self.tabs.addTab(self.tab_history, "历史记录")
        self.tabs.addTab(self.tab_about, "关于")
        
        layout.addWidget(self.tabs)
        
        self.setup_basic_tab()
        self.setup_ai_tab()
        self.setup_history_tab()
        self.setup_about_tab()
        
        # 底部按钮
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("保存并应用")
        self.btn_save.clicked.connect(self.save_and_apply)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_save)
        layout.addLayout(btn_layout)

    def setup_basic_tab(self):
        layout = QVBoxLayout(self.tab_basic)
        
        # 1. 模型选择
        layout.addWidget(QLabel("选择本地模型 (需已通过 Ollama 下载):"))
        self.combo_model = QComboBox()
        self.combo_model.setEditable(True) # 允许手动输入不在列表里的模型
        self.load_models()
        self.combo_model.setCurrentText(self.config["model_name"])
        layout.addWidget(self.combo_model)
        
        # 2. 大小调节
        layout.addWidget(QLabel("桌宠缩放大小 (0.5x - 2.0x):"))
        size_layout = QHBoxLayout()
        self.slider_size = QSlider(Qt.Horizontal)
        self.slider_size.setRange(50, 200) # 50% 到 200%
        self.slider_size.setValue(int(self.config["pet_size"] * 100))
        self.lbl_size_val = QLabel(f"{self.slider_size.value()}%")
        self.slider_size.valueChanged.connect(lambda v: self.lbl_size_val.setText(f"{v}%"))
        size_layout.addWidget(self.slider_size)
        size_layout.addWidget(self.lbl_size_val)
        layout.addLayout(size_layout)
        
        # 3. 日常台词频率
        layout.addWidget(QLabel("日常随机台词频率:"))
        self.combo_freq = QComboBox()
        self.combo_freq.addItems(["频繁 (1分钟)", "一般 (5分钟)", "较低 (10分钟)"])
        freq = self.config["daily_freq_minutes"]
        if freq == 1: self.combo_freq.setCurrentIndex(0)
        elif freq == 5: self.combo_freq.setCurrentIndex(1)
        elif freq == 10: self.combo_freq.setCurrentIndex(2)
        layout.addWidget(self.combo_freq)
        
        # 4. 漫游频率
        layout.addWidget(QLabel("桌面漫游频率 (走动):"))
        self.combo_wander = QComboBox()
        self.combo_wander.addItems(["关闭", "30 秒", "60 秒", "120 秒"])
        wander_sec = self.config.get("wander_freq_seconds", 60)
        if wander_sec == 0: self.combo_wander.setCurrentIndex(0)
        elif wander_sec == 30: self.combo_wander.setCurrentIndex(1)
        elif wander_sec == 60: self.combo_wander.setCurrentIndex(2)
        elif wander_sec == 120: self.combo_wander.setCurrentIndex(3)
        layout.addWidget(self.combo_wander)
        layout.addStretch()

    def load_models(self):
        self.combo_model.addItem("qwen2")
        try:
            models = ollama.list()
            # 兼容不同版本的 ollama 库返回格式
            model_list = models.get('models', []) if isinstance(models, dict) else models
            for m in model_list:
                name = m.get('name') if isinstance(m, dict) else m.model
                if name and name not in ["qwen2"]:
                    self.combo_model.addItem(name)
        except Exception:
            pass # 如果 Ollama 没启动，就只保留默认

    def setup_ai_tab(self):
        layout = QVBoxLayout(self.tab_ai)
        layout.addWidget(QLabel("System Prompt (角色设定):"))
        self.text_prompt = QTextEdit()
        self.text_prompt.setText(self.config["system_prompt"])
        layout.addWidget(self.text_prompt)

    def setup_history_tab(self):
        layout = QVBoxLayout(self.tab_history)
        layout.addWidget(QLabel("对话记录 (选中并点击下方按钮可删除):"))
        self.list_history = QListWidget()
        
        # 填充历史记录
        for i, msg in enumerate(self.config["history"]):
            role = "用户" if msg["role"] == "user" else "鲸鱼娘"
            text = msg["content"].replace('\n', ' ')
            item = QListWidgetItem(f"[{role}] {text}")
            item.setData(Qt.UserRole, i) # 存下真实索引
            self.list_history.addItem(item)
        
        layout.addWidget(self.list_history)
        
        btn_del = QPushButton("删除选中记录")
        btn_del.clicked.connect(self.delete_history)
        layout.addWidget(btn_del)

    def delete_history(self):
        current_row = self.list_history.currentRow()
        if current_row >= 0:
            # 从配置中删除
            real_index = self.list_history.item(current_row).data(Qt.UserRole)
            del self.config["history"][real_index]
            # 刷新列表
            self.list_history.takeItem(current_row)
            QMessageBox.information(self, "成功", "已删除该条记录，保存后生效。")

    def setup_about_tab(self):
        layout = QVBoxLayout(self.tab_about)
        text = QLabel("鲸鱼娘桌宠 v1.0\n\n基于 PyQt5 + Ollama 开发\n素材遵循 MIT 协议\n\n按 Ctrl+\\ 快捷键可隐藏/显示宠物\n点击下方按钮可彻底退出程序")
        text.setAlignment(Qt.AlignCenter)
        layout.addWidget(text)
        layout.addStretch()
        
        btn_exit = QPushButton("彻底退出程序")
        btn_exit.clicked.connect(self.parent_pet.close_program)
        layout.addWidget(btn_exit)

    def save_and_apply(self):
        model_name = self.combo_model.currentText().strip()
        if not model_name:
            QMessageBox.warning(self, "警告", "模型名称不能为空！请选择或输入正确的模型名。")
            return

        self.config["model_name"] = model_name
        self.config["pet_size"] = self.slider_size.value() / 100.0
        self.config["daily_freq_minutes"] = [1, 5, 10][self.combo_freq.currentIndex()]
        
        # === 新增：保存漫游频率 ===
        wander_idx = self.combo_wander.currentIndex()
        self.config["wander_freq_seconds"] = [0, 30, 60, 120][wander_idx]
        
        self.config["system_prompt"] = self.text_prompt.toPlainText()
        
        self.parent_pet.apply_settings()
        self.close()