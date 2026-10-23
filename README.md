# BookLive · AI 图书直播助手 V0.1

这是一个可运行的本地原型，包含：书库 CSV 导入、新增图书、口播稿生成、评论问答与推荐、试播指标计算。

**默认不需要 API Key。** 离线模式为模板生成与关键词匹配，仅供演示，不等于真实的大模型能力。

## Windows PowerShell 启动

```powershell
cd booklive_mvp
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

若没有 `py` 命令，先安装 Python 3.10+，或改用 `python`。
浏览器通常自动打开 `http://localhost:8501`。

## 使用真实大模型（可选）

先在 PowerShell 会话中设置环境变量，再启动网站：

```powershell
$env:OPENAI_API_KEY="你的API密钥"
$env:OPENAI_MODEL="gpt-4.1-mini"
.\.venv\Scripts\python.exe -m streamlit run app.py
```

在左侧开启「启用大模型生成」。模型需是你的 API 项目实际可用的型号，调用会产生费用。**不要把密钥写进源代码、CSV 或提交 GitHub。**

## 使用流程

1. 「书目管理」：先浏览示例虚构书目，再导入真实授权商品目录（UTF-8 CSV）。
2. 「直播介绍词」：选书，生成 30/60 秒口播草稿，人工核对。
3. 「评论问答与推荐」：粘贴一条模拟或获许可的评论，获得推荐候选。
4. 「试播记录」：录入真实试播指标，核算效率。

## 约束

- 演示书目是**虚构数据**，不代表任何实际商品和价格。
- 不自动抓取直播平台评论，也不代替人工发言、挂车或直播。
- 只使用得到授权的商品信息，不得擅自朗读图书正文。
- 推荐逻辑不应替代店员最终确认，尤其是儿童阅读建议、事实和商品信息。
- 本地 JSON 保存书库，不支持多用户并发；上线需换数据库和登录鉴权。

## 下一步可迭代

V0.2：语音 TTS 播报；V0.3：评论批量导入、历史记录；V0.4：接入店家获授权的数据源和权限机制；V0.5：多店铺 SaaS。
