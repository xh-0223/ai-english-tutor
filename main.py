import streamlit as st
import os
import time
from dotenv import load_dotenv
from audio_utils import (
    load_whisper_model, 
    load_language_tool, 
    AudioRecorder,
    speech_to_text, 
    evaluate_pronunciation, 
    correct_grammar,
    cleanup_temp_files
)
from llm_utils import init_deepseek_client, get_ai_response, generate_training_report

# -------------------------- 页面配置 --------------------------
st.set_page_config(
    page_title="AI英语口语陪练",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------- 加载环境变量和模型 --------------------------
@st.cache_resource
def load_all_models():
    """加载所有模型（只在第一次运行时执行）"""
    load_dotenv()
    
    whisper_model = load_whisper_model("small")
    language_tool = load_language_tool()
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    deepseek_client = None
    if api_key:
        try:
            deepseek_client = init_deepseek_client(api_key)
        except:
            st.warning("DeepSeek API Key无效，请检查.env文件")
    
    return whisper_model, language_tool, deepseek_client

# 加载模型
with st.spinner("正在加载模型，请稍候..."):
    whisper_model, language_tool, deepseek_client = load_all_models()

# 导入audio_utils并设置全局模型
import audio_utils
audio_utils.whisper_model = whisper_model
audio_utils.language_tool = language_tool

# -------------------------- 会话状态初始化（所有状态统一管理） --------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "scene" not in st.session_state:
    st.session_state.scene = "日常聊天"

if "difficulty" not in st.session_state:
    st.session_state.difficulty = "中级(B1-B2)"

if "recorder" not in st.session_state:
    st.session_state.recorder = AudioRecorder(max_duration=60)  # 最大录音60秒

if "recording" not in st.session_state:
    st.session_state.recording = False

if "processing" not in st.session_state:
    st.session_state.processing = False

if "last_result" not in st.session_state:
    st.session_state.last_result = None

# -------------------------- 侧边栏配置 --------------------------
with st.sidebar:
    st.title("🎤 AI英语口语陪练")
    st.divider()
    
    # 场景选择
    st.subheader("训练场景")
    scenes = {
        "日常聊天": "你是一位友好的美国大学生，正在和朋友聊天。用简单自然的英语回复，每次回复不要超过3句话。",
        "英文面试": "你是一位经验丰富的IT公司技术面试官，正在面试应聘软件工程师职位的候选人。用专业的英语提问和回复。",
        "餐厅点餐": "你是一家美国西餐厅的服务员，正在接待顾客点餐。用礼貌的英语回复。",
        "机场值机": "你是机场的值机柜台工作人员，正在为乘客办理登机手续。用清晰的英语回复。",
        "酒店入住": "你是酒店前台的工作人员，正在为客人办理入住手续。用友好的英语回复。"
    }
    st.session_state.scene = st.selectbox("选择场景", list(scenes.keys()))
    
    # 难度选择
    st.subheader("难度等级")
    st.session_state.difficulty = st.selectbox("选择难度", ["初级(A1-A2)", "中级(B1-B2)", "高级(C1-C2)"])
    
    # 麦克风设备选择
    st.subheader("麦克风设置")
    try:
        devices = AudioRecorder.get_available_devices()
        if devices:
            device_names = [f"{dev['index']}: {dev['name']}" for dev in devices]
            selected_device = st.selectbox("选择麦克风", device_names)
            selected_index = int(selected_device.split(":")[0])
            st.session_state.recorder.set_input_device(selected_index)
        else:
            st.warning("未检测到可用的麦克风设备")
    except Exception as e:
        st.error(f"获取麦克风设备失败：{str(e)}")
    
    st.divider()
    
    # 功能按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("清空对话", use_container_width=True):
            st.session_state.messages = []
            st.session_state.last_result = None
            cleanup_temp_files()  # 清空对话时删除所有临时文件
            st.rerun()
    
    with col2:
        if st.button("生成报告", use_container_width=True, disabled=not deepseek_client or len(st.session_state.messages) == 0):
            with st.spinner("正在生成训练报告..."):
                try:
                    report = generate_training_report(
                        deepseek_client,
                        st.session_state.scene,
                        st.session_state.difficulty,
                        st.session_state.messages
                    )
                    st.session_state.report = report
                    st.rerun()
                except Exception as e:
                    st.error(f"生成报告失败：{str(e)}")
    
    st.divider()
    
    # API状态
    if deepseek_client:
        st.success("✅ DeepSeek API已连接")
    else:
        st.error("❌ DeepSeek API未连接，请检查.env文件")

# -------------------------- 主界面 --------------------------
st.title(f"🎭 {st.session_state.scene} 口语训练")
st.subheader(f"难度等级：{st.session_state.difficulty}")
st.divider()

# 显示训练报告
if "report" in st.session_state:
    with st.expander("📊 你的口语训练报告", expanded=True):
        st.markdown(st.session_state.report)
        if st.button("关闭报告"):
            del st.session_state.report
            st.rerun()
    st.divider()

# 显示对话历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 显示上一次的录音结果（持久化显示，不会一闪而过）
if st.session_state.last_result:
    with st.chat_message("user"):
        st.audio(st.session_state.last_result["audio_path"], format="audio/wav")
        st.markdown(st.session_state.last_result["user_text"])
        
        col_score, col_correct = st.columns(2)
        with col_score:
            st.metric("发音评分", f"{st.session_state.last_result['accuracy']}分")
        with col_correct:
            if len(st.session_state.last_result["errors"]) > 0:
                st.warning(f"发现 {len(st.session_state.last_result['errors'])} 个语法错误")
                st.markdown(f"修正后：{st.session_state.last_result['corrected_text']}")
            else:
                st.success("语法完全正确！")

# -------------------------- 录音和对话功能（最终修复版） --------------------------
col1, col2 = st.columns([1, 5])

with col1:
    if not st.session_state.recording and not st.session_state.processing:
        if st.button("🎙️ 开始录音", use_container_width=True, type="primary"):
            # 开始新录音前，清理旧的临时文件（保留最近1个）
            cleanup_temp_files(keep_latest=1)
            
            st.session_state.recording = True
            st.session_state.recorder.start()
            st.session_state.last_result = None
            st.rerun()
    elif st.session_state.recording:
        if st.button("⏹️ 停止录音", use_container_width=True, type="secondary"):
            st.session_state.recording = False
            st.session_state.processing = True
            st.rerun()
    elif st.session_state.processing:
        st.info("正在处理录音...")

# 关键：在if块外面处理录音逻辑，确保一定会执行
if st.session_state.processing:
    try:
        # 停止录音并保存文件
        audio_path = st.session_state.recorder.stop()
        
        if not audio_path:
            st.error("❌ 录音失败，没有检测到声音")
            st.info("请检查麦克风是否正常工作，关闭其他占用麦克风的应用后重试")
        else:
            # 语音识别
            with st.spinner("正在识别语音..."):
                user_text = speech_to_text(audio_path)
            
            if not user_text:
                st.warning("⚠️ 没有识别到任何内容")
                st.info("请说清楚一点，确保麦克风离嘴10-20厘米，然后重新录制")
            else:
                # 发音评测
                accuracy = evaluate_pronunciation(user_text)
                
                # 语法纠错
                errors, corrected_text = correct_grammar(user_text)
                
                # 保存结果到会话状态（持久化）
                st.session_state.last_result = {
                    "audio_path": audio_path,
                    "user_text": user_text,
                    "accuracy": accuracy,
                    "errors": errors,
                    "corrected_text": corrected_text
                }
                
                # 添加到对话历史
                st.session_state.messages.append({"role": "user", "content": user_text})
                
                # AI回复
                if deepseek_client:
                    with st.chat_message("assistant"):
                        message_placeholder = st.empty()
                        full_response = ""
                        
                        try:
                            system_prompt = scenes[st.session_state.scene]
                            response = get_ai_response(deepseek_client, system_prompt, st.session_state.messages)
                            
                            for chunk in response:
                                if chunk.choices[0].delta.content:
                                    full_response += chunk.choices[0].delta.content
                                    message_placeholder.markdown(full_response + "▌")
                            
                            message_placeholder.markdown(full_response)
                            
                            # 添加到对话历史
                            st.session_state.messages.append({"role": "assistant", "content": full_response})
                        except Exception as e:
                            message_placeholder.error(f"AI回复失败：{str(e)}")
                            st.info("提示：这通常是因为DeepSeek API余额不足，请充值或注册新账号")
        
    except Exception as e:
        st.error(f"录音处理失败：{str(e)}")
        st.info("请检查麦克风权限，关闭其他占用麦克风的应用后重试")
    finally:
        # 重置处理状态（不再在这里删除文件！）
        st.session_state.processing = False
        st.rerun()

with col2:
    if not st.session_state.recording and not st.session_state.processing:
        st.info("点击左侧按钮开始录音，说完后点击停止按钮")
    elif st.session_state.recording:
        st.warning("正在录音中...点击停止按钮结束录音（最长60秒）")
    elif st.session_state.processing:
        st.info("正在处理录音，请稍候...")

# -------------------------- 页脚 --------------------------
st.divider()
st.caption("AI英语口语陪练 | 基于Streamlit和DeepSeek大模型")