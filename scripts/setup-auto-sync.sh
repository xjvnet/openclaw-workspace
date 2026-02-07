#!/bin/bash
#
# setup-auto-sync.sh - 设置自动同步定时任务
#

echo "🔄 Setting up OpenClaw auto-sync..."

# 确定同步间隔（分钟）
INTERVAL="${1:-5}"  # 默认5分钟

cat > /tmp/openclaw-sync-cron << EOF
# OpenClaw Auto Sync - 每${INTERVAL}分钟检查并同步
*/${INTERVAL} * * * * cd ~/.openclaw/workspace && bash scripts/auto-sync.sh >/dev/null 2>&1
EOF

echo ""
echo "📋 Cron job to be added:"
cat /tmp/openclaw-sync-cron
echo ""

read -p "Install this cron job? (y/N): " confirm
if [[ $confirm =~ ^[Yy]$ ]]; then
    # 添加到当前用户的 crontab
    (crontab -l 2>/dev/null | grep -v "openclaw-sync-cron\|auto-sync.sh"; cat /tmp/openclaw-sync-cron) | crontab -
    echo "✅ Cron job installed!"
    echo ""
    echo "📊 Current crontab:"
    crontab -l | grep -A1 "OpenClaw"
else
    echo "❌ Cancelled"
fi

rm /tmp/openclaw-sync-cron

echo ""
echo "💡 Manual commands:"
echo "   View logs:   tail -f ~/.openclaw/workspace/.auto-sync.log"
echo "   Run now:     bash ~/.openclaw/workspace/scripts/auto-sync.sh"
echo "   Edit cron:   crontab -e"
