# GLaDOS 云端自动签到服务

自动完成 GLaDOS 每日签到，获取免费时长积分。支持 GitHub Actions 云端运行，无需本地设备开机。

## 功能特性

- 自动每日签到获取时长积分
- 支持多种消息推送渠道（Server酱、PushPlus、Telegram）
- 随机延迟启动，降低风控风险
- 自动重试机制，提高成功率
- 识别已签到状态，避免重复告警

## 快速开始

### 1. 获取 Cookie

1. 登录 [GLaDOS 控制台](https://glados.cloud/console/checkin)
2. 按 `F12` 打开开发者工具
3. 切换到 `Network` 标签页
4. 刷新页面，找到任意请求
5. 在请求头中找到 `Cookie` 字段，复制完整值

### 2. 配置推送服务（可选）

选择以下任一推送服务：

**Server酱**
- 访问 [Server酱官网](https://sct.ftqq.com/) 获取 SendKey

**PushPlus**
- 访问 [PushPlus官网](http://www.pushplus.plus/) 获取 Token

**Telegram Bot**
- 创建 Bot 并获取 Token
- 获取 Chat ID

### 3. 本地运行

```bash
# 克隆仓库
git clone <your-repo-url>
cd GladosCheckin

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 Cookie 和推送配置

# 运行签到
python checkin.py
```

### 4. GitHub Actions 部署（推荐）

1. Fork 本仓库
2. 进入仓库 Settings → Secrets and variables → Actions
3. 添加以下 Secrets：
   - `GLADOS_COOKIE`: 你的 GLaDOS Cookie
   - `SERVERCHAN_KEY`: Server酱 Key（可选）
   - `PUSHPLUS_TOKEN`: PushPlus Token（可选）
   - `TELEGRAM_BOT_TOKEN`: Telegram Bot Token（可选）
   - `TELEGRAM_CHAT_ID`: Telegram Chat ID（可选）
4. 进入 Actions 页面，启用工作流
5. 等待定时触发或手动运行测试

## 环境变量说明

| 变量名 | 必需 | 说明 |
|--------|------|------|
| `GLADOS_COOKIE` | 是 | GLaDOS 网站完整 Cookie |
| `SERVERCHAN_KEY` | 否 | Server酱推送 Key |
| `PUSHPLUS_TOKEN` | 否 | PushPlus Token |
| `TELEGRAM_BOT_TOKEN` | 否 | Telegram Bot Token |
| `TELEGRAM_CHAT_ID` | 否 | Telegram Chat ID |

## 消息推送示例

**签到成功**
```
[签到成功]
获取积分: 5 天
总天数: 123 天
剩余时长: 456 天
```

**签到失败**
```
[签到失败]
错误原因: Cookie 已失效，请更新配置
```

## 注意事项

- Cookie 有效期通常为 1-3 个月，过期后需重新获取
- 建议不要在绝对固定时间签到，本项目已内置随机延迟
- 如遇签到失败，请检查 Cookie 是否过期

## License

MIT