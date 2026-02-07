# OpenClaw 多设备同步指南

## VPS 端（已完成 ✅）

```bash
cd ~/.openclaw/workspace

# 查看提交记录
git log --oneline

# 后续修改后同步
git add .
git commit -m "update: xxx"
git push origin master
```

---

## 本地电脑设置

### 1. 安装 OpenClaw

```bash
# macOS
brew install openclaw

# Linux
curl -fsSL https://openclaw.ai/install.sh | bash

# 验证
openclaw version
```

### 2. 克隆 Workspace

**方式 A：用 GitHub/GitLab（推荐）**

```bash
# 1. 先在 GitHub 创建仓库（如：你的用户名/openclaw-workspace）

# 2. VPS 端添加远程仓库
cd ~/.openclaw/workspace
git remote add origin https://github.com/你的用户名/openclaw-workspace.git
git push -u origin master

# 3. 本地电脑克隆
cd ~
mv ~/.openclaw/workspace ~/.openclaw/workspace.bak  # 备份默认的
git clone https://github.com/你的用户名/openclaw-workspace.git ~/.openclaw/workspace
```

**方式 B：直接 scp（不常用）**

```bash
# 从 VPS 下载
scp -r root@你的VPSIP:/root/.openclaw/workspace ~/.openclaw/
```

### 3. 安装自定义 Skills

```bash
# 安装 openclaw-backup skill
cd ~/.openclaw/workspace
openclaw skill install ./openclaw-backup.skill

# 或者重启 OpenClaw 让它自动加载 workspace/skills/
```

### 4. 配置验证

```bash
# 查看加载的 skills
openclaw skills list

# 测试
cd ~/.openclaw/workspace/skills/openclaw-backup
./scripts/backup.sh
```

---

## 日常使用流程

### 场景 1：在本地修改，同步到 VPS

```bash
# 本地电脑
cd ~/.openclaw/workspace
# 修改文件...
git add .
git commit -m "update: 添加新技能"
git push origin master

# VPS上拉取
cd ~/.openclaw/workspace
git pull origin master
```

### 场景 2：在 VPS 修改，同步到本地

```bash
# VPS
cd ~/.openclaw/workspace
# 修改文件...
git add .
git commit -m "update: 修改配置"
git push origin master

# 本地电脑拉取
cd ~/.openclaw/workspace
git pull origin master
```

---

## ⚠️ 注意事项

### 敏感文件不同步

`.gitignore` 已排除：
- `auth-profiles.json` - 认证信息（不同设备不同）
- `*.key`, `*.pem` - 密钥文件
- `.env` - 环境变量

**意味着**：
- 每台电脑需要单独配置 API key
- Notion/Discord 等 token 需要分别在本地和 VPS 设置

### 冲突解决

如果两边同时修改：

```bash
# 先拉取最新
git pull origin master

# 如有冲突，手动解决后
git add .
git commit -m "merge: 解决冲突"
git push origin master
```

---

## 快速检查清单

本地电脑安装后检查：

- [ ] `openclaw version` 正常
- [ ] `~/.openclaw/workspace` 有完整文件
- [ ] `SOUL.md`, `IDENTITY.md` 已同步（确认"你是谁"）
- [ ] `skills/` 目录下的 skills 可用
- [ ] `git status` 显示正常
- [ ] 配置好各服务的 auth（Notion, Discord 等）

---

## 下一步

1. **创建 GitHub 仓库**
2. **在本地电脑安装 OpenClaw**
3. **克隆 workspace**
4. **配置本地 auth**

需要我帮你配置哪一步？
