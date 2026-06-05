from audio_utils import load_whisper_model, load_language_tool, record_audio, speech_to_text, evaluate_pronunciation, correct_grammar
from llm_utils import init_deepseek_client, get_ai_response, generate_training_report
from dotenv import load_dotenv
import os

# 加载环境变量（你的DeepSeek API Key）
load_dotenv()

print("="*50)
print("🔧 正在加载所有模型...")
print("="*50)

# 1. 加载音频模型
whisper_model = load_whisper_model()
language_tool = load_language_tool()

# 2. 加载大模型
deepseek_client = init_deepseek_client(os.getenv("DEEPSEEK_API_KEY"))

# 3. 将模型传递给audio_utils模块
import audio_utils
audio_utils.whisper_model = whisper_model
audio_utils.language_tool = language_tool

print("\n✅ 所有模型加载完成！")
print("="*50)

# -------------------------- 测试1：录音和语音识别 --------------------------
print("\n=== 测试1：录音和语音识别 ===")
print("请准备好，5秒后开始录音，录音时长10秒")
print("请说一句简单的英语，比如：'Hello, my name is Tom. I am a student.'")
input("按回车键开始录音...")

audio_path = record_audio(record_seconds=10)
user_text = speech_to_text(audio_path)

print(f"\n🎤 你说的是：{user_text}")

# -------------------------- 测试2：发音评测 --------------------------
print("\n=== 测试2：发音评测 ===")
accuracy = evaluate_pronunciation(user_text)
print(f"📊 你的发音准确率：{accuracy}分")

if accuracy >= 90:
    print("🌟 太棒了！发音非常标准！")
elif accuracy >= 70:
    print("👍 不错！发音基本准确，还有提升空间")
else:
    print("💪 继续加油！多练习会越来越好")

# -------------------------- 测试3：语法纠错 --------------------------
print("\n=== 测试3：语法纠错 ===")
errors, corrected_text = correct_grammar(user_text)

if len(errors) == 0:
    print("✅ 语法完全正确！没有发现错误")
else:
    print(f"❌ 发现 {len(errors)} 个语法错误：")
    for i, error in enumerate(errors, 1):
        print(f"{i}. {error['original']} → {error['corrected']}")
        print(f"   说明：{error['message']}")
    
    print(f"\n✅ 修正后的句子：{corrected_text}")

# -------------------------- 测试4：AI对话 --------------------------
print("\n=== 测试4：AI对话 ===")
print("现在AI会根据你说的话进行回复")

# 系统提示词：模拟餐厅服务员
system_prompt = """
你是一家美国西餐厅的服务员，正在接待顾客点餐。
请用简单、自然的英语回复，每次回复不要超过3句话。
不要纠正用户的语法错误，专注于对话交流。
"""

# 对话历史
messages = [{"role": "user", "content": user_text}]

# 获取AI回复
response = get_ai_response(deepseek_client, system_prompt, messages, stream=False)
ai_reply = response.choices[0].message.content

print(f"\n🤖 AI服务员：{ai_reply}")

# -------------------------- 测试5：生成训练报告 --------------------------
print("\n=== 测试5：生成训练报告 ===")
print("正在生成你的口语训练报告...")

# 添加AI回复到对话历史
messages.append({"role": "assistant", "content": ai_reply})

# 生成报告
report = generate_training_report(
    deepseek_client,
    "餐厅点餐",
    "中级(B1-B2)",
    messages
)

print("\n" + "="*50)
print("📊 你的口语训练报告")
print("="*50)
print(report)
print("="*50)

print("\n🎉 所有测试完成！你的后端模块全部正常工作！")