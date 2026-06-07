import pyaudio
import wave
import whisper
import Levenshtein
import language_tool_python
import string
import threading
import os
import time
import uuid

# -------------------------- 全局模型变量（在main.py中初始化） --------------------------
whisper_model = None
language_tool = None

# -------------------------- 模型加载函数（只调用一次） --------------------------
def load_whisper_model(model_size="small"):
    """加载Whisper语音识别模型，增加错误处理"""
    try:
        return whisper.load_model(model_size, download_root="./models")
    except Exception as e:
        raise RuntimeError(f"Whisper模型加载失败：{str(e)}")

def load_language_tool():
    """加载LanguageTool语法纠错模型，增加错误处理"""
    try:
        return language_tool_python.LanguageTool('en-US')
    except Exception as e:
        raise RuntimeError(f"LanguageTool模型加载失败：{str(e)}")

# -------------------------- 1. 无阻塞录音功能（全版本兼容+唯一文件名） --------------------------
class AudioRecorder:
    """线程安全的音频录制器，兼容所有PyAudio版本，使用唯一文件名避免冲突"""
    def __init__(self, sample_rate=16000, max_duration=60):
        self.sample_rate = sample_rate
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.max_duration = max_duration  # 最大录音时长（秒）
        self.recording = False
        self.frames = []
        self.thread = None
        self.p = None
        self.stream = None
        self.input_device_index = None
        self.current_filename = None  # 保存当前录音的唯一文件名

    @staticmethod
    def get_available_devices():
        """获取所有可用的麦克风设备列表"""
        p = pyaudio.PyAudio()
        devices = []
        for i in range(p.get_device_count()):
            dev_info = p.get_device_info_by_index(i)
            if dev_info.get('maxInputChannels') > 0:
                devices.append({
                    'index': i,
                    'name': dev_info.get('name'),
                    'channels': dev_info.get('maxInputChannels')
                })
        p.terminate()
        return devices

    def set_input_device(self, device_index):
        """设置要使用的麦克风设备"""
        self.input_device_index = device_index

    def start(self):
        """开始录音，生成唯一文件名"""
        if self.recording:
            return False
        
        # 生成唯一文件名（避免文件被提前删除）
        self.current_filename = f"temp_{uuid.uuid4().hex[:8]}.wav"
        
        self.recording = True
        self.frames = []
        self.thread = threading.Thread(target=self._record_loop, daemon=True)
        self.thread.start()
        return True

    def stop(self):
        """停止录音并保存文件，增加文件完整性检查"""
        if not self.recording:
            return None
        
        self.recording = False
        self.thread.join(timeout=2.0)  # 最多等待2秒，防止线程卡死
        
        # 确保资源被正确释放
        if self.stream:
            try:
                if self.stream.is_active():
                    self.stream.stop_stream()
                self.stream.close()
            except:
                pass
        
        if self.p:
            try:
                self.p.terminate()
            except:
                pass
        
        # 检查是否有录音数据
        if len(self.frames) == 0:
            return None
        
        # 保存录音文件（使用唯一文件名）
        try:
            wf = wave.open(self.current_filename, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(pyaudio.get_sample_size(self.format))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(self.frames))
            wf.close()
        except Exception as e:
            raise RuntimeError(f"录音文件保存失败：{str(e)}")
        
        # 等待文件完全写入磁盘
        time.sleep(0.3)
        
        # 检查文件是否存在且不为空
        if os.path.exists(self.current_filename) and os.path.getsize(self.current_filename) > 100:
            return self.current_filename
        else:
            return None

    def _record_loop(self):
        """录音循环，兼容所有PyAudio版本"""
        try:
            self.p = pyaudio.PyAudio()
            
            # 打开音频流（移除所有不兼容参数）
            stream_kwargs = {
                'format': self.format,
                'channels': self.channels,
                'rate': self.sample_rate,
                'input': True,
                'frames_per_buffer': self.chunk
            }
            
            if self.input_device_index is not None:
                stream_kwargs['input_device_index'] = self.input_device_index
            
            self.stream = self.p.open(**stream_kwargs)
            
            # 预热麦克风，跳过前0.5秒的噪音
            time.sleep(0.5)
            
            start_time = time.time()
            while self.recording:
                # 检查是否超过最大录音时长
                if time.time() - start_time > self.max_duration:
                    print(f"已达到最大录音时长{self.max_duration}秒，自动停止")
                    self.recording = False
                    break
                
                # 兼容所有版本的读取方式
                try:
                    data = self.stream.read(self.chunk)
                    self.frames.append(data)
                except IOError:
                    # 忽略缓冲区溢出错误
                    continue
                
        except Exception as e:
            print(f"录音线程异常：{str(e)}")
        finally:
            self.recording = False

# -------------------------- 2. 语音识别功能（终极优化版） --------------------------
def speech_to_text(audio_path):
    """
    将语音文件转换为英文文本，增加多项稳定性改进
    :param audio_path: 录音文件路径
    :return: 识别出的文本
    """
    # 等待文件存在并可访问
    for _ in range(20):
        if os.path.exists(audio_path) and os.path.getsize(audio_path) > 100:
            break
        time.sleep(0.1)
    else:
        raise FileNotFoundError(f"录音文件不存在或为空：{audio_path}")
    
    try:
        result = whisper_model.transcribe(
            audio_path, 
            language="en",  # 强制指定英语，避免语言检测错误
            temperature=0.0,
            fp16=False,
            verbose=False,
            condition_on_previous_text=False  # 避免上下文干扰
        )
        text = result["text"].strip()
        
        # 过滤空结果和无意义的结果
        if not text or len(text) < 2:
            return ""
        
        return text
    except Exception as e:
        raise RuntimeError(f"语音识别失败：{str(e)}")

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

# -------------------------- 4. 语法纠错功能（全版本兼容修复版） --------------------------
def correct_grammar(text):
    """
    检查并纠正英语语法、拼写和标点错误，兼容所有language_tool_python版本
    :param text: 用户输入的文本
    :return: 错误列表、修正后的文本
    """
    if not text:
        return [], ""
    
    try:
        matches = language_tool.check(text)
        corrected_text = language_tool_python.utils.correct(text, matches)

        errors = []
        for match in matches:
            if match.replacements:
                # 兼容新旧版本的Match对象属性
                if hasattr(match, 'length'):
                    error_length = match.length
                elif hasattr(match, 'errorLength'):
                    error_length = match.errorLength
                else:
                    error_length = 0
                
                errors.append({
                    "original": text[match.offset:match.offset+error_length],
                    "corrected": match.replacements[0],
                    "message": match.message
                })

        return errors, corrected_text
    except Exception as e:
        print(f"语法纠错失败：{str(e)}")
        return [], text

# -------------------------- 5. 清理临时文件（智能清理） --------------------------
def cleanup_temp_files(keep_latest=None):
    """
    清理所有临时录音文件
    :param keep_latest: 保留最新的N个文件，避免删除正在使用的文件
    """
    temp_files = [f for f in os.listdir('.') if f.startswith('temp_') and f.endswith('.wav')]
    
    if keep_latest and len(temp_files) > keep_latest:
        # 按修改时间排序，保留最新的keep_latest个
        temp_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        temp_files = temp_files[keep_latest:]
    
    for file in temp_files:
        try:
            os.remove(file)
        except:
            pass