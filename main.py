import streamlit as st
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 页面配置
st.set_page_config(
    page_title="AI英语口语陪练",
    page_icon="🎤",
    layout="wide"
)

# 侧边栏
st.sidebar.title("🎯 训练设置")
scenes = {
    "英文面试": "你是一位经验丰富的IT公司技术面试官，正在面试应聘软件工程师职位的候选人。",
    "餐厅点餐": "你是一家美国西餐厅的服务员，正在接待顾客点餐。",
    "机场值机": "你是机场的值机柜台工作人员，正在为乘客办理登机手续。"
}
selected_scene = st.sidebar.selectbox("选择训练场景", list(scenes.keys()))
difficulty = st.sidebar.select_slider("英语水平", ["初级(A1-A2)", "中级(B1-B2)", "高级(C1-C2)"], "中级(B1-B2)")
speech_rate = st.sidebar.slider("AI语速", -50, +50, 0, step=10)

# 主界面
st.title("🎤 AI英语口语陪练")
st.subheader(f"当前场景：{selected_scene} | 难度：{difficulty}")

# 对话历史容器
chat_container = st.container()

# 底部录音按钮
record_button = st.button("🎙️ 开始录音", type="primary", use_container_width=True)

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示对话历史
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])