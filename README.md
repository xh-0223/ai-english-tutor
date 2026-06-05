# AI英语口语陪练

一个基于Streamlit和DeepSeek大模型的智能英语口语陪练应用，支持实时录音、语音识别、发音评测、语法纠错和AI对话功能。

## 功能特点

- 🎙️ **实时录音**：支持10秒固定时长录音
- 🗣️ **语音识别**：使用OpenAI Whisper模型，识别准确
- 📊 **发音评测**：综合发音评分（0-100分）
- ✅ **语法纠错**：自动检查英语语法、拼写错误
- 🤖 **AI对话**：多场景英文对话陪练
- 📝 **训练报告**：自动生成口语评分与改进建议
- 🎭 **场景支持**：面试、餐厅、机场等实用场景
- 🎚️ **难度可调**：初级/中级/高级

## 快速开始

### 1. 安装依赖
```bash
python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
2. 安装 FFmpeg（必须）
bash
运行
choco install ffmpeg -y
3. 配置 API Key
新建 .env 文件：
plaintext
DEEPSEEK_API_KEY=你的DeepSeek Key
4. 运行测试
bash
运行
python test_all.py
5. 启动 Web 界面
bash
运行
streamlit run main.py
项目结构
audio_utils.py 录音、识别、发音评测、语法纠错
llm_utils.py AI 对话、报告生成
test_all.py 后端功能完整测试
main.py 前端界面
requirements.txt 依赖包
已完成功能 ✅
✅ 录音功能
✅ 语音识别
✅ 发音评分
✅ 语法纠错
✅ AI 对话模块
✅ 训练报告生成
✅ 项目完整结构
常见问题
找不到 FFmpeg → 安装后重启 VS Code
API 402 错误 → DeepSeek 余额不足
依赖报错 → 重新运行安装命令
