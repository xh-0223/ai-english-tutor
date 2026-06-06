import pyaudio
import wave
import whisper
import Levenshtein
import language_tool_python
import string
import threading
import os
import time

# -------------------------- 全局模型变量（在main.py中初始化） --------------------------
whisper_model = None
language_tool = None

# -------------------------- 模型加载函数（只调用一次） --------------------------
def load_whisper_model(model_size="small"):
    """加载Whisper语音识别模型"""
    return whisper.load_model(model_size)

def load_language_tool():
    """加载LanguageTool语法纠错模型"""
    return language_tool_python.LanguageTool('en-US')

# -------------------------- 1. 无阻塞录音功能（线程安全版） --------------------------
class AudioRecorder:
    """线程安全的音频录制器"""
    def __init__(self, filename="user_input.wav", sample_rate=16000):
        self.filename = filename
        self.sample_rate = sample_rate
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.recording = False
        self.frames = []
        self.thread = None
        self.p = None
        self.stream = None

    def start(self):
        """开始录音"""
        if self.recording:
            return
        
        self.recording = True
        self.frames = []
        self.thread = threading.Thread(target=self._record_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """停止录音并保存文件"""
        if not self.recording:
            return
        
        self.recording = False
        self.thread.join()  # 等待录音线程结束
        
        # 保存录音文件
        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.format))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        
        # 确保文件被正确关闭
        time.sleep(0.1)
        
        return self.filename

    def _record_loop(self):
        """录音循环（在单独线程中运行）"""
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.format,
                                  channels=self.channels,
                                  rate=self.sample_rate,
                                  input=True,
                                  frames_per_buffer=self.chunk)
        
        while self.recording:
            data = self.stream.read(self.chunk)
            self.frames.append(data)
        
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

# -------------------------- 2. 语音识别功能（优化版） --------------------------
def speech_to_text(audio_path):
    """
    将语音文件转换为英文文本
    :param audio_path: 录音文件路径
    :return: 识别出的文本
    """
    # 等待文件存在并可访问
    for _ in range(10):
        if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
            break
        time.sleep(0.1)
    else:
        raise FileNotFoundError(f"录音文件不存在或为空：{audio_path}")
    
    result = whisper_model.transcribe(
        audio_path, 
        language="en", 
        temperature=0.0,
        fp16=False  # 禁用FP16，避免CPU警告
    )
    return result["text"].strip()

# -------------------------- 3. 优化版发音评测功能 --------------------------
def evaluate_pronunciation(user_text, expected_text=""):
    """
    评测用户发音准确率（单词级+字符级+长度惩罚综合评分）
    :param user_text: 用户识别出的文本
    :param expected_text: 期望的正确文本（可选）
    :return: 准确率(0-100)
    """
    def clean_text(text):
        """清理文本：移除标点，转为小写，去除多余空格"""
        text = text.translate(str.maketrans('', '', string.punctuation))
        return ' '.join(text.strip().lower().split())
    
    if not user_text:
        return 0
    
    user_clean = clean_text(user_text)
    expected_clean = clean_text(expected_text) if expected_text else user_clean

    # 计算单词级准确率（占60%权重）
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

    # 长度匹配惩罚（占10%权重）
    length_ratio = min(len(user_words), len(expected_words)) / max(len(user_words), len(expected_words)) if expected_words else 1
    length_accuracy = int(length_ratio * 100)

    # 综合评分
    total_accuracy = int(word_accuracy * 0.6 + char_accuracy * 0.3 + length_accuracy * 0.1)
    return max(0, min(100, total_accuracy))

# -------------------------- 4. 语法纠错功能（优化版） --------------------------
def correct_grammar(text):
    """
    检查并纠正英语语法、拼写和标点错误
    :param text: 用户输入的文本
    :return: 错误列表、修正后的文本
    """
    if not text:
        return [], ""
    
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

# -------------------------- 5. 清理临时文件 --------------------------
def cleanup_temp_files():
    """清理临时录音文件"""
    temp_files = ["user_input.wav", "ai_response.mp3"]
    for file in temp_files:
        if os.path.exists(file):
            try:
                os.remove(file)
            except:
                pass