# SSH部署指南 - Traffic Light Conversation Tagging System

## 当前问题
SSH推送失败：`Permission denied (publickey)`

## 可能原因
1. SSH公钥未添加到GitHub账户
2. 仓库不存在
3. 没有仓库访问权限
4. SSH代理未运行

## 解决方案

### 方案1：检查并添加SSH密钥到GitHub

#### 1.1 查看SSH公钥
```bash
# 查看现有的SSH公钥
cat ~/.ssh/id_ed25519.pub
# 或
cat ~/.ssh/id_rsa.pub
```

#### 1.2 复制公钥内容
公钥格式类似：
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... user@host
```
或
```
ssh-rsa AAAAB3NzaC1lZDI1NTE5AAAAI... user@host
```

#### 1.3 添加到GitHub
1. 登录GitHub (https://github.com)
2. 点击右上角头像 → Settings
3. 左侧菜单选择 "SSH and GPG keys"
4. 点击 "New SSH key"
5. 标题: "Windows OpenClaw"
6. 密钥类型: Authentication Key
7. 粘贴公钥内容
8. 点击 "Add SSH key"

### 方案2：测试SSH连接
```bash
# 测试连接
ssh -T git@github.com

# 期望输出：
# Hi quick123-666! You've successfully authenticated, but GitHub does not provide shell access.
```

### 方案3：启动SSH代理
```bash
# 启动SSH代理
eval $(ssh-agent -s)

# 添加SSH密钥
ssh-add ~/.ssh/id_ed25519
# 或
ssh-add ~/.ssh/id_rsa
```

### 方案4：检查仓库是否存在

#### 4.1 通过浏览器检查
访问：https://github.com/quick123-666/TrafficLight-Conversation-Tagging-System-skill

#### 4.2 如果仓库不存在，需要创建
1. 登录GitHub
2. 访问 https://github.com/quick123-666
3. 点击 "New repository"
4. 仓库名: `TrafficLight-Conversation-Tagging-System-skill`
5. 描述: "红绿灯对话标记系统 - 用于AI助手任务评分"
6. 选择 Public 或 Private
7. **不要初始化** README、.gitignore 或 license
8. 点击 "Create repository"

### 方案5：使用HTTPS+Personal Access Token

如果SSH仍然不行，使用HTTPS+Token：

#### 5.1 生成GitHub Personal Access Token
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 点击 "Generate new token (classic)"
3. 备注: "TrafficLight Deployment"
4. 过期时间: 90天
5. 权限: 勾选 "repo" (全部仓库权限)
6. 点击 "Generate token"
7. **立即复制token**（只显示一次）

#### 5.2 使用Token推送
```bash
# 更改远程URL为HTTPS+Token格式
git remote set-url origin https://quick123-666:YOUR_TOKEN@github.com/quick123-666/TrafficLight-Conversation-Tagging-System-skill.git

# 推送
git push -u origin master
```

### 方案6：手动创建仓库并推送

如果上述方法都失败，手动创建：

#### 6.1 在GitHub创建空仓库
- 名称: `TrafficLight-Conversation-Tagging-System-skill`
- 不要初始化任何文件

#### 6.2 使用提供的命令
GitHub创建后会显示推送命令：
```bash
git remote add origin git@github.com:quick123-666/TrafficLight-Conversation-Tagging-System-skill.git
git branch -M master
git push -u origin master
```

## 当前本地状态
```bash
# 检查当前状态
cd "C:\Users\Administrator\assistants\assistant-1\skills\task-scorekeeper"
git status
git log --oneline -5
git remote -v
```

## 文件已准备就绪
- ✅ `traffic_light.py` - 红绿灯评分主程序
- ✅ `SKILL.md` - 完整技能说明
- ✅ `DEPLOYMENT.md` - 部署指南
- ✅ `SSH_DEPLOYMENT_GUIDE.md` - 本文件
- ✅ 所有测试文件和文档

## 紧急备用方案
如果所有方法都失败，可以将整个目录打包发送：
```bash
# 创建ZIP文件
cd "C:\Users\Administrator\assistants\assistant-1\skills"
Compress-Archive -Path task-scorekeeper -DestinationPath trafficlight-skill.zip
```

然后通过其他方式（邮件、网盘等）传输文件。