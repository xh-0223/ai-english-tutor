from openai import OpenAI

def init_deepseek_client(api_key):
    """初始化DeepSeek大模型客户端（完全兼容所有版本）"""
    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

def get_ai_response(client, system_prompt, messages, stream=True):
    """
    获取AI流式回复
    :param client: DeepSeek客户端
    :param system_prompt: 角色设定提示词
    :param messages: 对话历史
    :param stream: 是否流式输出
    :return: AI回复流
    """
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=full_messages,
        temperature=0.7,
        stream=stream
    )
    return response

def generate_training_report(client, scene, difficulty, messages):
    """
    生成详细的课后训练报告
    :param client: DeepSeek客户端
    :param scene: 训练场景
    :param difficulty: 难度等级
    :param messages: 对话历史
    :return: 完整的报告文本
    """
    summary_prompt = f"""
    请根据以下英语对话记录，为用户生成一份专业的口语训练报告：
    对话场景：{scene}
    难度等级：{difficulty}
    
    对话记录：
    {messages}
    
    请严格按照以下格式生成报告：
    ## 一、整体评分
    综合得分：XX/100
    CEFR等级：A1/A2/B1/B2/C1/C2
    
    ## 二、能力维度评分
    - 发音：XX/100
    - 语法：XX/100
    - 流利度：XX/100
    - 词汇量：XX/100
    - 逻辑表达：XX/100
    
    ## 三、本次训练亮点
    1. 
    2. 
    3. 
    
    ## 四、存在的不足
    1. 
    2. 
    3. 
    
    ## 五、针对性改进建议
    1. 
    2. 
    3. 
    
    要求：
    1. 评分要客观合理，基于对话内容
    2. 亮点和不足要具体，不要泛泛而谈
    3. 改进建议要可操作，有针对性
    4. 全部用中文回复
    """

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": summary_prompt}],
        temperature=0.5,
        stream=False
    )
    return response.choices[0].message.content