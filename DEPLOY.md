# BookLive AI 公开试用版部署指南

## 最快方案：Streamlit Community Cloud

1. 解压 ZIP，将 `booklive_mvp` 文件夹内的 `app.py`、`engine.py`、`requirements.txt`、`data/books.json`、`.gitignore` 上传到你自己的 GitHub 仓库根目录（不要上传 .venv 或 API Key）。
2. 打开 https://share.streamlit.io ，使用 GitHub 登录，选择 **Create app** → 选择仓库 → 分支 `main` → 主文件 `app.py`。
3. 给公开网站选择一个可用子域名，点击 **Deploy**；部署完成后获得固定网址，如 `https://你的名称.streamlit.app`。
4. 用手机流量/无痕浏览窗口打开网址测试分享效果。公开免费体验版默认只读，不需要 API Key。

## 若想启用真实 AI

在部署后台 **Advanced settings / Secrets** 填入（自行使用真实密钥）：

```toml
OPENAI_API_KEY = "sk-..."
OPENAI_MODEL = "gpt-4.1-mini"
```

Streamlit secrets 不会自动等价于操作系统环境变量，因此此项目启动时从 `st.secrets` 读取并映射为环境变量。切勿把密钥放进 GitHub 或发送给客户。公开网站开放真实 AI 将产生 API 费用，需要在账户端设置支出限制并注意刷量风险。

## 编辑模式

公开模式默认 `BOOKLIVE_ALLOW_EDIT=0`，防止访客任意改写图书数据。仅在信任的私有环境设置 `BOOKLIVE_ALLOW_EDIT=1` 以启用新增和 CSV 导入。Streamlit 免费云托管的本地文件修改不能作为可靠的长期数据库，不适合真实多用户后台；后续需要独立持久数据库与登录权限。

## 当前不支持

- 尚无语音播报
- 不接直播平台、不自动抓评论
- 没有真实客户账号/权限机制
- 仍需人工审核对外话术
