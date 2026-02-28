---
name: openclaw-backup
description: 备份和恢复 OpenClaw 配置、技能、命令和设置。跨设备同步，使用 git 进行版本控制，自动化备份，并迁移到新机器。
metadata: {"openclaw":{"emoji":"💾","requires":{"bins":["git","tar","rsync","cron"],"env":[]}}}
---

# OpenClaw Backup Skill

备份、恢复和跨设备同步您的 OpenClaw 配置。

## 概述

本技能帮助您：
- 备份所有 OpenClaw 数据和设置
- 从备份恢复
- 多台机器之间同步
- 对配置进行版本控制
- 自动化备份任务
- 迁移到新设备

---

## OpenClaw 目录结构

### 关键位置

```
~/.openclaw/                    # OpenClaw 主目录
├── openclaw.json               # 主配置文件
├── credentials/                # 凭据（需要加密备份）
├── cron/                       # 定时任务配置
├── memory/                     # 记忆数据库
├── agents/                     # Agent 配置
├── devices/                    # 设备配置
└── workspace/                  # 用户工作区
    ├── AGENTS.md               # Agent 说明
    ├── SOUL.md                 # 灵魂/人格配置
    ├── USER.md                 # 用户信息
    ├── TOOLS.md                # 工具配置
    ├── HEARTBEAT.md            # 心跳配置
    ├── IDENTITY.md             # 身份配置
    ├── SESSION-STATE.md        # 会话状态
    ├── skills/                 # 自定义技能
    │   ├── skill-name/
    │   │   └── SKILL.md
    │   └── another-skill/
    ├── memory/                 # 日常记忆文件
    └── .git/                   # Git 仓库（如果有）
```

### 备份什么

```
必须备份（始终备份）：
✓ ~/.claude/workspace/skills/   # 自定义技能
✓ ~/.claude/workspace/AGENTS.md # Agent 配置
✓ ~/.claude/workspace/SOUL.md   # 人格配置
✓ ~/.claude/workspace/USER.md   # 用户信息
✓ ~/.claude/workspace/TOOLS.md  # 工具配置
✓ ~/.claude/openclaw.json       # 主配置
✓ ~/.claude/cron/               # 定时任务
✓ ~/.claude/agents/             # Agent 配置

推荐备份（通常备份）：
✓ ~/.claude/workspace/memory/   # 记忆文件
✓ ~/.claude/workspace/identity/ # 身份配置
✓ ~/.claude/devices/            # 设备配置

可选（按情况）：
○ ~/.claude/credentials/        # 凭据（需加密）
○ ~/.claude/openclaw.json.bak*  # 备份文件
○ ~/.claude/logs/               # 日志文件
○ ~/.claude/memory/             # LanceDB 数据库（可重建）
```

---

## 快速备份命令

### 完整备份

```bash
# 创建带时间戳的备份
BACKUP_DIR="$HOME/openclaw-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="openclaw_backup_$TIMESTAMP"

mkdir -p "$BACKUP_DIR"

tar -czvf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" \
  -C "$HOME" \
  .openclaw/openclaw.json \
  .openclaw/workspace/skills \
  .openclaw/workspace/AGENTS.md \
  .openclaw/workspace/SOUL.md \
  .openclaw/workspace/USER.md \
  .openclaw/workspace/TOOLS.md \
  .openclaw/workspace/HEARTBEAT.md \
  .openclaw/workspace/IDENTITY.md \
  .openclaw/cron \
  .openclaw/agents \
  .openclaw/devices \
  2>/dev/null

echo "Backup created: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
```

### 快速技能备份

```bash
# 仅备份技能
tar -czvf ~/openclaw_skills_$(date +%Y%m%d).tar.gz \
  -C "$HOME" \
  .openclaw/workspace/skills
```

### 从备份恢复

```bash
# 恢复完整备份
BACKUP_FILE="$HOME/openclaw-backups/openclaw_backup_20260129.tar.gz"

# 先预览内容
tar -tzvf "$BACKUP_FILE"

# 恢复（会覆盖现有文件）
tar -xzvf "$BACKUP_FILE" -C "$HOME"

echo "Restore complete!"
```

---

## 备份脚本

### 完整功能备份脚本

```bash
#!/bin/bash
# openclaw-backup.sh - OpenClaw 备份工具

set -e

# 配置
BACKUP_ROOT="${OPENCLAW_BACKUP_DIR:-$HOME/openclaw-backups}"
CLAUDE_DIR="$HOME/.openclaw"
WORKSPACE_DIR="$CLAUDE_DIR/workspace"
MAX_BACKUPS=10
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# 检查目录
check_dirs() {
    if [ ! -d "$CLAUDE_DIR" ]; then
        log_error "OpenClaw 目录不存在: $CLAUDE_DIR"
        exit 1
    fi
}

# 创建备份
create_backup() {
    local backup_type="${1:-full}"
    local backup_name="openclaw_${backup_type}_${TIMESTAMP}"
    local backup_path="$BACKUP_ROOT/$backup_name.tar.gz"
    
    mkdir -p "$BACKUP_ROOT"
    
    log_info "创建 $backup_type 备份..."
    
    case $backup_type in
        full)
            tar -czvf "$backup_path" \
                -C "$HOME" \
                .openclaw/openclaw.json \
                .openclaw/workspace/skills \
                .openclaw/workspace/AGENTS.md \
                .openclaw/workspace/SOUL.md \
                .openclaw/workspace/USER.md \
                .openclaw/workspace/TOOLS.md \
                .openclaw/workspace/HEARTBEAT.md \
                .openclaw/workspace/IDENTITY.md \
                .openclaw/cron \
                .openclaw/agents \
                .openclaw/devices \
                2>/dev/null || true
            ;;
        skills)
            tar -czvf "$backup_path" \
                -C "$HOME" \
                .openclaw/workspace/skills \
                .openclaw/workspace/AGENTS.md \
                2>/dev/null || true
            ;;
        config)
            tar -czvf "$backup_path" \
                -C "$HOME" \
                .openclaw/openclaw.json \
                .openclaw/workspace/AGENTS.md \
                .openclaw/workspace/SOUL.md \
                .openclaw/workspace/USER.md \
                .openclaw/workspace/TOOLS.md \
                .openclaw/workspace/HEARTBEAT.md \
                .openclaw/workspace/IDENTITY.md \
                .openclaw/agents \
                .openclaw/devices \
                2>/dev/null || true
            ;;
        memory)
            tar -czvf "$backup_path" \
                -C "$HOME" \
                .openclaw/workspace/memory \
                2>/dev/null || true
            ;;
        *)
            log_error "未知备份类型: $backup_type"
            exit 1
            ;;
    esac
    
    if [ -f "$backup_path" ]; then
        local size=$(du -h "$backup_path" | cut -f1)
        log_info "备份已创建: $backup_path ($size)"
    else
        log_error "备份失败!"
        exit 1
    fi
}

# 列出备份
list_backups() {
    log_info "可用备份位置: $BACKUP_ROOT"
    echo ""
    
    if [ -d "$BACKUP_ROOT" ]; then
        ls -lh "$BACKUP_ROOT"/*.tar.gz 2>/dev/null | \
            awk '{print $9, $5, $6, $7, $8}' || \
            echo "未找到备份."
    else
        echo "备份目录不存在."
    fi
}

# 恢复备份
restore_backup() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        log_error "请指定备份文件"
        list_backups
        exit 1
    fi
    
    # 尝试不同路径
    if [ ! -f "$backup_file" ]; then
        backup_file="$BACKUP_ROOT/$backup_file"
    fi
    
    if [ ! -f "$backup_file" ]; then
        # 尝试找最新的
        backup_file=$(ls -t "$BACKUP_ROOT"/*.tar.gz 2>/dev/null | head -1)
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_error "备份文件不存在: $backup_file"
        exit 1
    fi
    
    log_warn "这将覆盖现有配置!"
    read -p "继续? (y/N) " confirm
    
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        log_info "恢复已取消."
        exit 0
    fi
    
    log_info "恢复自: $backup_file"
    tar -xzvf "$backup_file" -C "$HOME"
    log_info "恢复完成!"
}

# 清理旧备份
cleanup_backups() {
    log_info "清理旧备份 (保留最近 $MAX_BACKUPS 个)..."
    
    cd "$BACKUP_ROOT" 2>/dev/null || return
    
    local count=$(ls -1 *.tar.gz 2>/dev/null | wc -l)
    
    if [ "$count" -gt "$MAX_BACKUPS" ]; then
        local to_delete=$((count - MAX_BACKUPS))
        ls -1t *.tar.gz | tail -n "$to_delete" | xargs rm -v
        log_info "已删除 $to_delete 个旧备份"
    else
        log_info "无需清理 ($count 个备份)"
    fi
}

# 显示统计
show_stats() {
    log_info "OpenClaw 备份统计"
    echo ""
    
    echo "=== 目录大小 ==="
    du -sh "$WORKSPACE_DIR"/skills 2>/dev/null || echo "Skills: N/A"
    du -sh "$WORKSPACE_DIR" 2>/dev/null || echo "Workspace: N/A"
    du -sh "$CLAUDE_DIR" 2>/dev/null || echo "Total: N/A"
    
    echo ""
    echo "=== 技能统计 ==="
    find "$WORKSPACE_DIR/skills" -name "SKILL.md" 2>/dev/null | wc -l | xargs echo "技能数量:"
    
    echo ""
    echo "=== 备份目录 ==="
    if [ -d "$BACKUP_ROOT" ]; then
        du -sh "$BACKUP_ROOT"
        ls -1 "$BACKUP_ROOT"/*.tar.gz 2>/dev/null | wc -l | xargs echo "备份文件:"
    else
        echo "暂无备份"
    fi
}

# 使用说明
usage() {
    cat << EOF
OpenClaw 备份工具

用法: $(basename $0) <命令> [选项]

命令:
    backup [类型]   创建备份 (类型: full, skills, config, memory)
    restore <文件>  从备份恢复
    list            列出可用备份
    cleanup         清理旧备份 (保留最近 $MAX_BACKUPS 个)
    stats           显示备份统计
    help            显示帮助

示例:
    $(basename $0) backup              # 完整备份
    $(basename $0) backup skills       # 仅技能
    $(basename $0) backup config       # 仅配置
    $(basename $0) restore latest.tar.gz
    $(basename $0) list
    $(basename $0) cleanup

环境变量:
    OPENCLAW_BACKUP_DIR    备份目录 (默认: ~/openclaw-backups)

EOF
}

# 主函数
main() {
    check_dirs
    
    case "${1:-help}" in
        backup)
            create_backup "${2:-full}"
            ;;
        restore)
            restore_backup "$2"
            ;;
        list)
            list_backups
            ;;
        cleanup)
            cleanup_backups
            ;;
        stats)
            show_stats
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            log_error "未知命令: $1"
            usage
            exit 1
            ;;
    esac
}

main "$@"
```

### 保存和使用

```bash
# 保存脚本
mkdir -p ~/.local/bin
cat > ~/.local/bin/openclaw-backup << 'SCRIPT'
# 粘贴上面的脚本内容
SCRIPT

chmod +x ~/.local/bin/openclaw-backup

# 使用
openclaw-backup backup          # 完整备份
openclaw-backup backup skills   # 仅技能
openclaw-backup backup config   # 仅配置
openclaw-backup list            # 列出备份
openclaw-backup restore <文件>  # 恢复
```

---

## Git 版本控制

### 初始化 Git 仓库

```bash
cd ~/.openclaw/workspace

# 初始化 git
git init

# 创建 .gitignore
cat > .gitignore << 'EOF'
# 机器特定设置
SESSION-STATE.md

# 缓存和临时文件
*.tmp
*.log
*.bak*

# 大文件
*.tar.gz
*.zip

# 敏感数据
credentials/
.credentials/
.DS_Store

# 数据库
memory/lancedb/
EOF

# 初始提交
git add .
git commit -m "Initial OpenClaw configuration backup"
```

### 推送到远程

```bash
# 添加远程仓库 (GitHub, GitLab 等)
git remote add origin git@github.com:username/openclaw-config.git

# 推送
git push -u origin main
```

### 每日工作流

```bash
# 修改技能/设置后
cd ~/.openclaw/workspace
git add .
git commit -m "Updated skill: trading-bot"
git push
```

### 自动提交脚本

```bash
#!/bin/bash
# auto-commit-openclaw.sh - 自动提交更改

cd ~/.openclaw/workspace || exit 1

# 检查更改
if git diff --quiet && git diff --staged --quiet; then
    echo "没有需要提交的更改"
    exit 0
fi

# 获取更改的文件用于提交消息
CHANGED=$(git status --short | head -5 | awk '{print $2}' | tr '\n' ', ')

git add .
git commit -m "Auto-backup: $CHANGED ($(date +%Y-%m-%d))"
git push 2>/dev/null || echo "推送失败 (离线?)"
```

---

## 跨设备同步

### 方法 1: Git 同步

```bash
# 在新设备上
git clone git@github.com:username/openclaw-config.git ~/.openclaw/workspace

# 拉取最新更改
cd ~/.openclaw/workspace && git pull

# 推送本地更改
cd ~/.openclaw/workspace && git add . && git commit -m "Update" && git push
```

### 方法 2: Rsync

```bash
# 同步到远程服务器
rsync -avz --delete \
    ~/.openclaw/workspace/ \
    user@server:~/openclaw-backup/workspace/

# 从远程服务器同步
rsync -avz --delete \
    user@server:~/openclaw-backup/workspace/ \
    ~/.openclaw/workspace/
```

### 方法 3: 云存储

```bash
# 备份到云文件夹 (Dropbox, Google Drive 等)
CLOUD_DIR="$HOME/Dropbox/openclaw"

# 同步技能
rsync -avz ~/.openclaw/workspace/skills/ "$CLOUD_DIR/skills/"

# 复制配置
cp ~/.openclaw/workspace/AGENTS.md "$CLOUD_DIR/"
cp ~/.openclaw/workspace/SOUL.md "$CLOUD_DIR/"
```

### 同步脚本

```bash
#!/bin/bash
# sync-openclaw.sh - 跨设备同步 OpenClaw 配置

SYNC_DIR="${OPENCLAW_SYNC_DIR:-$HOME/Dropbox/openclaw}"
WORKSPACE_DIR="$HOME/.openclaw/workspace"

sync_to_cloud() {
    echo "同步到云端..."
    mkdir -p "$SYNC_DIR"
    
    rsync -avz --delete "$WORKSPACE_DIR/skills/" "$SYNC_DIR/skills/"
    rsync -avz "$WORKSPACE_DIR/AGENTS.md" "$SYNC_DIR/"
    rsync -avz "$WORKSPACE_DIR/SOUL.md" "$SYNC_DIR/"
    rsync -avz "$WORKSPACE_DIR/USER.md" "$SYNC_DIR/"
    rsync -avz "$WORKSPACE_DIR/TOOLS.md" "$SYNC_DIR/"
    rsync -avz "$WORKSPACE_DIR/HEARTBEAT.md" "$SYNC_DIR/" 2>/dev/null
    
    echo "同步完成!"
}

sync_from_cloud() {
    echo "从云端同步..."
    
    rsync -avz "$SYNC_DIR/skills/" "$WORKSPACE_DIR/skills/"
    rsync -avz "$SYNC_DIR/AGENTS.md" "$WORKSPACE_DIR/"
    rsync -avz "$SYNC_DIR/SOUL.md" "$WORKSPACE_DIR/"
    rsync -avz "$SYNC_DIR/USER.md" "$WORKSPACE_DIR/"
    rsync -avz "$SYNC_DIR/TOOLS.md" "$WORKSPACE_DIR/"
    rsync -avz "$SYNC_DIR/HEARTBEAT.md" "$WORKSPACE_DIR/" 2>/dev/null
    
    echo "同步完成!"
}

case "$1" in
    push) sync_to_cloud ;;
    pull) sync_from_cloud ;;
    *)
        echo "用法: $0 {push|pull}"
        echo "  push - 上传本地配置到云端"
        echo "  pull - 下载云端配置到本地"
        ;;
esac
```

---

## 自动化备份

### Cron 任务 (Linux/Mac)

```bash
# 编辑 crontab
crontab -e

# 每天凌晨 2 点完整备份
0 2 * * * /home/user/.local/bin/openclaw-backup backup full

# 每周日凌晨 3 点清理
0 3 * * 0 /home/user/.local/bin/openclaw-backup cleanup

# 每 6 小时自动 git 提交
0 */6 * * * cd ~/.openclaw/workspace && git add . && git commit -m "Auto-backup $(date +\%Y-\%m-\%d)" && git push 2>/dev/null
```

### Systemd 定时器 (Linux)

```bash
# 创建服务: ~/.config/systemd/user/openclaw-backup.service
cat > ~/.config/systemd/user/openclaw-backup.service << 'EOF'
[Unit]
Description=OpenClaw Backup

[Service]
Type=oneshot
ExecStart=/home/user/.local/bin/openclaw-backup backup full
EOF

# 创建定时器: ~/.config/systemd/user/openclaw-backup.timer
cat > ~/.config/systemd/user/openclaw-backup.timer << 'EOF'
[Unit]
Description=Daily OpenClaw Backup

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
EOF

# 启用
systemctl --user enable openclaw-backup.timer
systemctl --user start openclaw-backup.timer
```

### Launchd (macOS)

```bash
# 创建 plist: ~/Library/LaunchAgents/com.openclaw.backup.plist
cat > ~/Library/LaunchAgents/com.openclaw.backup.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.backup</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/username/.local/bin/openclaw-backup</string>
        <string>backup</string>
        <string>full</string>
    </array>
    <key>RunAtLoad</key>
    <false/>
    <key>StartCalendarInterval</key>
    <array>
        <dict>
            <key>Hour</key>
            <integer>2</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
    </array>
</dict>
</plist>
EOF

# 加载
launchctl load ~/Library/LaunchAgents/com.openclaw.backup.plist
```

---

## 迁移到新机器

### 完整迁移步骤

```bash
# 1. 在旧机器上创建完整备份
openclaw-backup backup full

# 2. 将备份传输到新机器
# 方法 A: 使用 rsync
rsync -avz ~/openclaw-backups/ user@new-machine:~/openclaw-backups/

# 方法 B: 使用 scp
scp ~/openclaw-backups/openclaw_full_*.tar.gz user@new-machine:~/openclaw-backups/

# 方法 C: 从 Git 拉取
# 在新机器上
git clone git@github.com:username/openclaw-config.git ~/.openclaw/workspace

# 3. 在新机器上恢复
cd ~
openclaw-backup restore openclaw_full_20260129_120000.tar.gz

# 4. 验证安装
openclaw status

# 5. 重启服务（如需要）
openclaw gateway restart
```

### 增量迁移（推荐）

```bash
# 如果使用 Git 同步
# 在新机器上
cd ~/.openclaw/workspace
git clone git@github.com:username/openclaw-config.git temp_workspace

# 移动文件
cp -r temp_workspace/* ~/.openclaw/workspace/
rm -rf temp_workspace

# 安装依赖的技能
clawhub sync  # 如有 clawhub

# 验证
openclaw status
```

---

## 故障排除

### 常见问题

**备份太大？**
```bash
# 排除日志和缓存
tar -czvf backup.tar.gz \
  --exclude='.openclaw/logs' \
  --exclude='.openclaw/memory/lancedb' \
  ...
```

**权限错误？**
```bash
# 检查权限
ls -la ~/.openclaw/

# 修复权限
chmod -R 700 ~/.openclaw/credentials
chmod 600 ~/.openclaw/openclaw.json
```

**Git 冲突？**
```bash
# 查看冲突
git status

# 接受 ours 或 theirs
git checkout --ours path/to/file
# 或
git checkout --theirs path/to/file

# 然后提交
git add .
git commit -m "Resolve conflict"
```

---

## 快速命令参考

| 操作 | 命令 |
|------|------|
| 完整备份 | `openclaw-backup backup full` |
| 仅技能 | `openclaw-backup backup skills` |
| 仅配置 | `openclaw-backup backup config` |
| 列出备份 | `openclaw-backup list` |
| 恢复 | `openclaw-backup restore <file>` |
| 清理旧备份 | `openclaw-backup cleanup` |
| 查看统计 | `openclaw-backup stats` |
| 自动 git 提交 | `cd ~/.openclaw/workspace && git add . && git commit -m "update" && git push` |