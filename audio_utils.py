import pyaudio
import wave
import whisper
import Levenshtein
import language_tool_python
import string

# -------------------------- 全局模型变量（在main.py中初始化） --------------------------
whisper_model = None
language_tool = None

# -------------------------- 模型加载函数（只调用一次） --------------------------
def load_whisper_model():
    """加载Whisper语音识别模型（第一次运行会自动下载460MB模型文件）"""
    return whisper.load_model("small")

def load_language_tool():
    """加载LanguageTool语法纠错模型（第一次运行会自动下载200MB服务）"""
    return language_tool_python.LanguageTool('en-US')

# -------------------------- 1. 录音功能 --------------------------
def record_audio(filename="user_input.wav", sample_rate=16000, record_seconds=10):
    """
    录制用户语音，保存为WAV格式
    :param filename: 保存的文件名
    :param sample_rate: 采样率（Whisper推荐16000Hz）
    :param record_seconds: 录音时长（秒）
    :return: 录音文件路径
    """
    chunk = 1024
    format = pyaudio.paInt16
    channels = 1

    p = pyaudio.PyAudio()
    stream = p.open(format=format,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=chunk)

    frames = []
    print("🎙️ 正在录音...")

    # 固定时长录音（后续队友B会改成点击停止）
    for i in range(0, int(sample_rate / chunk * record_seconds)):
        data = stream.read(chunk)
        frames.append(data)

    print("✅ 录音结束！")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(format))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()

    return filename

# -------------------------- 2. 语音识别功能 --------------------------
def speech_to_text(audio_path):
    """
    将语音文件转换为英文文本
    :param audio_path: 录音文件路径
    :return: 识别出的文本
    """
    result = whisper_model.transcribe(audio_path, language="en", temperature=0.0)
    return result["text"].strip()

# -------------------------- 3. 发音评测功能（优化版） --------------------------
def evaluate_pronunciation(user_text, expected_text=""):
    """
    评测用户发音准确率（单词级+字符级综合评分）
    :param user_text: 用户识别出的文本
    :param expected_text: 期望的正确文本（可选）
    :return: 准确率(0-100)
    """
    def clean_text(text):
        """清理文本：移除标点，转为小写"""
        text = text.translate(str.maketrans('', '', string.punctuation))
        return text.strip().lower()
    
    if not user_text:
        return 0
    
    user_clean = clean_text(user_text)
    expected_clean = clean_text(expected_text) if expected_text else user_clean

    # 计算单词级准确率（占70%权重）
    user_words = user_clean.split()
    expected_words = expected_clean.split()
    
    correct_words = 0
    for u_word, e_word in zip(user_words, expected_words):
        if u_word == e_word:
            correct_words += 1
    
    word_accuracy = int(correct_words / len(expected_words) * 100) if expected_words else 100

    # 计算字符级Levenshtein距离（占30%权重）
    char_distance = Levenshtein.distance(user_clean, expected_clean)
    max_char_length = max(len(user_clean), len(expected_clean))
    char_accuracy = int((1 - char_distance / max_char_length) * 100) if max_char_length else 100

    # 综合评分
    total_accuracy = int(word_accuracy * 0.7 + char_accuracy * 0.3)
    return max(0, min(100, total_accuracy))

# -------------------------- 4. 语法纠错功能 --------------------------
def correct_grammar(text):
    """
    检查并纠正英语语法、拼写和标点错误
    :param text: 用户输入的文本
    :return: 错误列表、修正后的文本
    """
    matches = language_tool.check(text)
    corrected_text = language_tool_python.utils.correct(text, matches)

    errors = []
    for match in matches:
        if match.replacements:
            errors.append({
                "original": text[match.offset:match.offset+match.length],
                "corrected": match.replacements[0],
                "message": match.message
            })

    return errors, corrected_text