#!/bin/bash
#
# openclaw-backup.sh - Backup OpenClaw configuration, workspace, and skills
#

set -e

BACKUP_DIR="${1:-$HOME/openclaw-backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="openclaw-backup-${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

echo "📦 Creating OpenClaw backup..."
echo "   Destination: ${BACKUP_PATH}"

# Create backup directory
mkdir -p "${BACKUP_PATH}"

# Detect OpenClaw directories
OPENCLAW_DIR="${OPENCLAW_DIR:-$HOME/.openclaw}"
AGENTS_DIR="${AGENTS_DIR:-$OPENCLAW_DIR/agents}"
WORKSPACE_DIR="${WORKSPACE_DIR:-$OPENCLAW_DIR/workspace}"
SKILLS_GLOBAL="${SKILLS_GLOBAL:-/usr/lib/node_modules/openclaw/skills}"

echo ""
echo "📋 Backup Contents:"

# 1. Backup configuration
echo "   📁 Configuration (~/.openclaw)"
if [ -d "$OPENCLAW_DIR" ]; then
    cp -r "$OPENCLAW_DIR" "${BACKUP_PATH}/openclaw-config"
    echo "      ✓ Config backed up"
else
    echo "      ⚠ Config directory not found"
fi

# 2. Backup workspace (if exists and not in .openclaw)
if [ -d "$WORKSPACE_DIR" ] && [ "$WORKSPACE_DIR" != "$OPENCLAW_DIR/workspace" ]; then
    echo "   📁 Workspace"
    cp -r "$WORKSPACE_DIR" "${BACKUP_PATH}/workspace"
    echo "      ✓ Workspace backed up"
fi

# 3. Backup global skills (optional - may require sudo)
echo "   📁 Global Skills (optional)"
if [ -d "$SKILLS_GLOBAL" ]; then
    # Try to backup without sudo first
    if cp -r "$SKILLS_GLOBAL" "${BACKUP_PATH}/skills-global" 2>/dev/null; then
        echo "      ✓ Global skills backed up"
    else
        echo "      ⚠ Global skills require elevated permissions (skipped)"
    fi
fi

# 4. Create metadata file
cat > "${BACKUP_PATH}/backup-metadata.json" << EOF
{
  "timestamp": "${TIMESTAMP}",
  "date_iso": "$(date -Iseconds)",
  "backup_name": "${BACKUP_NAME}",
  "hostname": "$(hostname)",
  "user": "$(whoami)",
  "openclaw_dir": "${OPENCLAW_DIR}",
  "workspace_dir": "${WORKSPACE_DIR}",
  "version": {
    "openclaw": "$(openclaw version 2>/dev/null || echo 'unknown')",
    "node": "$(node --version 2>/dev/null || echo 'unknown')"
  }
}
EOF

echo "      ✓ Metadata created"

# 5. Create archive
echo ""
echo "📦 Creating archive..."
cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
rm -rf "$BACKUP_NAME"

BACKUP_SIZE=$(du -h "${BACKUP_NAME}.tar.gz" | cut -f1)
echo ""
echo "✅ Backup complete!"
echo "   Archive: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
echo "   Size: ${BACKUP_SIZE}"
echo ""
echo "💡 To restore, run:"
echo "   openclaw-backup-restore ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
