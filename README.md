# 🐋 鲸鱼娘桌宠 (Whale Pet)

一款基于 **PyQt5** 与 **Ollama 本地大模型** 的 AI 桌面宠物。
（素材来源于大肥鱼，由一只不知道大肥鱼就是自己的D老师完成的代码）
她是一只可爱的蓝鲸女仆（名字由你的 System Prompt 决定），不仅能陪你聊天，还能在桌面上随机漫步，甚至拥有“长期记忆”！

![宠物预览](assets/0.png)

## ✨ 核心特性

- **🖥️ 桌面常驻与互动**：无边框透明窗口，支持鼠标拖拽移动、左键点击挥手，右键唤起聊天面板。
- **🤖 接入本地大模型**：通过 Ollama 连接本地 LLM，支持**流式输出**（打字机效果），回复不卡顿。自动过滤 `思考` 思维链标签。
- **🧠 智能记忆压缩**：突破上下文限制！对话超过 20 轮时，自动将早期对话总结为【前情摘要】并拼接到系统设定中，让她永远记得你。
- **💬 丰富的预设台词**：内置大量带有 AI 圈梗的日常台词、时间问候（早/中/晚/凌晨）、点击与拖拽互动，且**不污染 AI 聊天历史**。
- **🚶 桌面随机漫游**：支持让宠物在桌面上随机走动（自带两帧走路动画），漫游频率可在设置中自定义（30s/60s/120s/关闭）。
- **⚙️ 完善的设置面板**：独立设置窗口，支持动态获取本地模型列表、调节宠物大小、修改 System Prompt、管理并删除特定历史记录、查看简介等。
- **📝 配置持久化**：重启程序后，你的设定、大小缩放和对话记忆都不会丢失。
- **⌨️ 全局快捷键**：支持 `Ctrl + \` 全局隐藏/显示宠物，摸鱼时一键遁地，不留痕迹。

## 🛠️ 环境准备

在运行本项目之前，请确保你的电脑上已安装：

1. **Python 3.9+**
2. **Ollama** (用于本地大模型运行)
   - 请前往 [Ollama 官网](https://ollama.com/) 下载并安装。
   - 安装后，在终端运行以下命令拉取默认模型（本项目默认使用 `qwen2`，你也可以在设置里换成别的）：
     ```bash
     ollama run qwen2
     ```

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/你的用户名/你的仓库名.git
cd 你的仓库名
```

### 2. 创建并激活虚拟环境

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install PyQt5 ollama requests keyboard
```

### 4. 启动桌宠

```bash
python main.py
```

*启动后，她会根据当前时间主动和你打招呼哦！右键点击她可以打开聊天框。
按 `Ctrl + \` 快捷键可以随时隐藏/显示宠物；如需彻底退出程序，请在设置窗口的“关于”页面点击退出。*

## 📂 项目结构

```text
whale-pet/
├── assets/              # 宠物图片素材 (站立、走路、挥手等)
├── .gitignore           # Git 忽略配置 (忽略 venv 和 config.json)
├── config.py            # 配置文件读写模块
├── main.py              # 程序主入口，包含 UI 与核心交互逻辑
├── presets.py           # 本地预设台词库
├── settings_dialog.py   # 独立设置窗口 UI
└── README.md            # 项目说明
```

## 🎨 自定义与配置

- **修改台词**：你可以直接编辑 `presets.py` 文件，加入属于你自己的专属梗。
- **修改设定**：右键宠物 -> 点击 ⚙️ -> 切换到“AI 设定”页，在这里修改 System Prompt 即可改变她的性格。
- **数据存储**：程序运行时会在根目录生成 `config.json` 文件，存放你的对话历史和设置。该文件已加入 `.gitignore`，不会泄露到 GitHub。

## 🙏 致谢

- **图片素材**：取自 [dsh-client-ui-pet](https://github.com/xituisuany-max/dsh-client-ui-pet) (遵循 MIT 开源协议)。
- **框架与库**：感谢 PyQt5 与 Ollama 提供的优秀工具。

## 📄 开源协议

本项目基于 [MIT License](https://opensource.org/licenses/MIT) 开源。