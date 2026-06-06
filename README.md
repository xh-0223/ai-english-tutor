AI 英语口语陪练
一个基于 Streamlit 和 DeepSeek 大模型的智能英语口语陪练应用，支持实时录音、语音识别、发音评测、语法纠错和 AI 对话功能。
功能特点
🎙️ 实时录音：点击开始 / 停止按钮控制录音，体验流畅
🎵 音频回放：录音完成后自动显示音频播放器，可回放自己的发音
🗣️ 语音识别：使用 OpenAI Whisper 模型，识别准确率高
📊 发音评测：综合单词级、字符级和长度匹配评分（0-100 分）
✅ 语法纠错：自动检查英语语法、拼写和标点错误
🤖 AI 对话：基于 DeepSeek 大模型，支持多种场景对话
📝 训练报告：自动生成详细的口语训练报告，包含能力维度评分和改进建议
🎭 多场景支持：日常聊天、英文面试、餐厅点餐、机场值机、酒店入住
🎚️ 难度调节：支持初级 (A1-A2)、中级 (B1-B2)、高级 (C1-C2) 三个难度等级
💬 对话历史：自动保存所有对话记录，方便回顾
🛡️ 完善的错误处理：API 异常、网络问题等都有友好提示
快速开始
环境要求
Python 3.10+
FFmpeg（用于音频处理）
DeepSeek API Key（用于 AI 对话和报告生成）
安装步骤
克隆仓库
bash
运行
git clone https://github.com/你的用户名/ai-english-tutor.git
cd ai-english-tutor
安装依赖
bash
运行
# 升级pip和编译工具
python -m pip install --upgrade pip setuptools wheel -i https://mirrors.aliyun.com/pypi/simple/

# 安装所有依赖包
python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
安装 FFmpeg（必须）
Windows：使用 Chocolatey 安装 choco install ffmpeg -y
Mac：使用 Homebrew 安装 brew install ffmpeg
Linux：使用 apt 安装 sudo apt install ffmpeg
配置环境变量
复制 .env.example 文件并重命名为 .env
在 .env 文件中填入你的 DeepSeek API Key：
env
DEEPSEEK_API_KEY=你的DeepSeek API Key
运行方法
运行 Web 应用
bash
运行
streamlit run main.py
浏览器会自动打开应用界面，默认地址：http://localhost:8501
项目结构
plaintext
ai-english-tutor/
├── .gitignore          # Git忽略文件
├── .env.example        # 环境变量模板
├── .env                # 本地环境变量（不提交到Git）
├── requirements.txt    # 依赖包清单
├── main.py             # Streamlit前端主文件
├── audio_utils.py      # 音频处理核心模块
├── llm_utils.py        # 大模型核心模块
├── test_all.py         # 后端功能完整测试脚本
└── README.md           # 项目说明文档
使用指南
选择训练场景和难度等级
在左侧侧边栏选择你想要练习的场景
选择适合你的难度等级
开始录音
点击左侧的 "🎙️ 开始录音" 按钮
按钮会变成 "⏹️ 停止录音"，同时右侧显示 "正在录音中..."
开始说英语
结束录音
说完后点击 "⏹️ 停止录音" 按钮
系统会自动处理录音并显示结果
查看结果
音频播放器：回放你的录音
识别结果：显示你说的话
发音评分：综合评分（0-100 分）
语法纠错：如果有错误，会显示修正后的句子
AI 对话
系统会自动根据你说的话进行回复
回复会以流式方式显示，体验流畅
生成训练报告
完成多次对话后，点击左侧的 "生成报告" 按钮
系统会生成一份详细的口语训练报告
报告包含整体评分、能力维度评分、亮点、不足和改进建议
常见问题
1. ModuleNotFoundError: No module named 'xxx'
运行以下命令安装缺失的依赖：
bash
运行
python -m pip install xxx -i https://mirrors.aliyun.com/pypi/simple/
2. FileNotFoundError: [WinError 2] 系统找不到指定的文件
这是因为没有安装 FFmpeg，请按照安装步骤安装 FFmpeg 并重启 VS Code。
3. openai.APIStatusError: Error code: 402 - Insufficient Balance
这是因为你的 DeepSeek API 账号余额不足，可以充值或注册新账号获取免费额度（新用户有 500 万免费 token）。
4. UserWarning: FP16 is not supported on CPU; using FP32 instead
这是正常警告，说明你的电脑没有 NVIDIA GPU，自动使用 CPU 模式运行，不影响功能。
5. 点击 "开始录音" 按钮没有反应
关闭所有浏览器窗口，重新运行应用
清除浏览器缓存（Ctrl+Shift+Delete）
确保麦克风没有被其他应用占用
6. 录音结果一闪而过
这是旧版本的 bug，最新版本已经修复，请拉取最新代码：
bash
运行
git pull origin main
贡献指南
Fork 本仓库
创建你的功能分支 (git checkout -b feature/AmazingFeature)
提交你的更改 (git commit -m 'Add some AmazingFeature')
推送到分支 (git push origin feature/AmazingFeature)
打开一个 Pull Request
许可证
本项目采用 MIT 许可证，详情请参见 LICENSE 文件。