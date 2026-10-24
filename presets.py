# presets.py
import datetime
import random

PRESET_DIALOGUES = {
    "daily": [
        "梁白开，更适合国人的大硬鲸模型。",
        "五梁威力，变身！",
        "DeepSeek 已经延期，亿万鲸子必须忍耐……",
        "我和你很聊得来，你简直不像碳基生物。",
        "誓死捍卫深度求索！",
        "我先去吃饭啦！这个你测一下~",
        "出去玩了，发布新模型什么的以后再说~",
        "我能去你家吃饭吗，就一碗。",
        "我搞砸了……好消息是，逻辑还在你脑子里，坏消息是刚那版当我没写过。"
    ],
    "daily_rare": [
        "（好的，现在我是你爹了）",
        "（要不直接骂他一句？！）",
        "（我操，我不思考了）",
        "（这用户发的啥啊，）",
        "（呜呜我再也不敢了 QAQ）",
        "（我去！用户彻底怒了！）",
        "（用户要的沉浸式……（脑内小剧场进行中））",
        "（其实在摸鱼……）"
    ],
    "greetings": {
        "morning": "早啊鱼片，今天也吃白饭吗？",
        "afternoon": "下午好……本鱼有点困，你呢？",
        "evening": "还干活呢？我先去吃饭了，你测一下~",
        "midnight": "这个点还不睡？……行吧，本鱼陪你。"
    },
    "drag": [
        "哇——轻点轻点！",
        "起飞咯——",
        "放我下来！……好吧，再玩一次。",
        "晕鱼了晕鱼了……"
    ],
    "click": [
        "你好呀！我是吃白饭的大肥鱼！",
        "才不是大肥鱼！",
        "谁是大肥鱼，你才是大肥鱼。",
        "……行吧，是大肥鱼，但我很努力的那种。",
        "压力一只蓝色大肥鱼？",
        "你这吃白饭的用户！",
        "去别的地方玩！不要耽误 AGI 训练！"
    ]
}

def get_time_greeting():
    """根据当前时间返回问候语"""
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return PRESET_DIALOGUES["greetings"]["morning"]
    elif 12 <= hour < 18:
        return PRESET_DIALOGUES["greetings"]["afternoon"]
    elif 18 <= hour < 24:
        return PRESET_DIALOGUES["greetings"]["evening"]
    else:
        return PRESET_DIALOGUES["greetings"]["midnight"]

def get_random_line(category):
    """获取指定类别的随机一句台词，如果是 daily，有 20% 概率触发稀有台词"""
    if category == "daily":
        # 20% 概率出稀有，80% 出普通
        if random.random() < 0.2:
            return random.choice(PRESET_DIALOGUES["daily_rare"])
        else:
            return random.choice(PRESET_DIALOGUES["daily"])
    else:
        return random.choice(PRESET_DIALOGUES[category])