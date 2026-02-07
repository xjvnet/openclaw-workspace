#!/bin/bash
#
# auto-sync.sh - 自动同步 OpenClaw workspace 到 GitHub
#

WORKSPACE_DIR="${WORKSPACE_DIR:-$HOME/.openclaw/workspace}"
LOG_FILE="$WORKSPACE_DIR/.auto-sync.log"
LOCK_FILE="/tmp/openclaw-auto-sync.lock"

# 防止重复运行
if [ -f "$LOCK_FILE" ]; then
    PID=$(cat "$LOCK_FILE" 2>/dev/null)
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "[$(date)] Auto-sync already running (PID: $PID)" >> "$LOG_FILE"
        exit 0
    fi
fi
echo $$ > "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

cd "$WORKSPACE_DIR" || exit 1

# 检查是否有远程仓库
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "[$(date)] ERROR: No remote origin configured" >> "$LOG_FILE"
    exit 1
fi

# 检查网络连接
if ! curl -s https://github.com > /dev/null; then
    echo "[$(date)] Network unavailable, skipping sync" >> "$LOG_FILE"
    exit 0
fi

echo "[$(date)] Checking for changes..." >> "$LOG_FILE"

# 先拉取远程更新（避免冲突）
if ! git pull origin main >> "$LOG_FILE" 2>&1; then
    echo "[$(date)] WARNING: Pull failed, may have conflicts" >> "$LOG_FILE"
fi

# 检查本地是否有改动
if [ -z "$(git status --porcelain)" ]; then
    echo "[$(date)] No local changes" >> "$LOG_FILE"
    exit 0
fi

# 自动提交
git add . >> "$LOG_FILE" 2>&1

# 生成提交信息（列出改动的文件）
CHANGED=$(git diff --cached --name-only | head -5 | tr '\n' ', ')
if [ -z "$CHANGED" ]; then
    CHANGED="auto-sync"
fi

COMMIT_MSG="sync: $(date '+%Y-%m-%d %H:%M') - ${CHANGED%,}"

if git commit -m "$COMMIT_MSG" >> "$LOG_FILE" 2>&1; then
    echo "[$(date)] Committed: $COMMIT_MSG" >> "$LOG_FILE"
    
    # 推送到远程
    if git push origin main >> "$LOG_FILE" 2>&1; then
        echo "[$(date)] ✅ Pushed to origin/main" >> "$LOG_FILE"
    else
        echo "[$(date)] ❌ Push failed" >> "$LOG_FILE"
    fi
else
    echo "[$(date)] Commit failed or nothing to commit" >> "$LOG_FILE"
fi

echo "---" >> "$LOG_FILE"
