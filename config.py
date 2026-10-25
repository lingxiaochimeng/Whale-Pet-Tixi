# config.py
import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "model_name": "qwen2",
    "system_prompt": "你是一只可爱的鲸鱼娘女仆，名字叫小蓝。你说话语气活泼、带一点海洋气息（比如偶尔提到尾巴、水），每次回答尽量简短（50字以内）。不要在回复中输出时间。",
    "history": [],
    "pet_size": 1.0,
    "daily_freq_minutes": 5
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for k, v in DEFAULT_CONFIG.items():
                    # 如果键不存在，或者值为空(None/空字符串)，就用默认值
                    if k not in data or data[k] is None or data[k] == "":
                        data[k] = v
                return data
        except Exception:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)