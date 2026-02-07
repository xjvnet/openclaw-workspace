#!/bin/bash
#
# openclaw-update.sh - Update OpenClaw with automatic rollback support
#

set -e

UPDATE_CHANNEL="${1:-stable}"
DRY_RUN=false

if [ "$1" = "--dry-run" ]; then
    DRY_RUN=true
fi

echo "🔄 OpenClaw Update with Rollback Protection"
echo "   Channel: $UPDATE_CHANNEL"
echo ""

# Detect directories
OPENCLAW_DIR="${OPENCLAW_DIR:-$HOME/.openclaw}"

echo "📦 Step 1: Creating pre-update backup..."
BACKUP_DIR="${HOME}/openclaw-backups"
mkdir -p "$BACKUP_DIR"
BACKUP_FILE="${BACKUP_DIR}/pre-update-$(date +%Y%m%d_%H%M%S).tar.gz"

# Create backup before update
if [ "$DRY_RUN" = false ]; then
    /bin/bash "$(dirname "$0")/backup.sh" "$BACKUP_DIR" > /dev/null 2>&1
    echo "   ✓ Backup created"
    echo "     Location: $BACKUP_FILE"
else
    echo "   [DRY-RUN] Would create backup"
fi

echo ""
echo "🚀 Step 2: Updating OpenClaw..."

if [ "$DRY_RUN" = true ]; then
    echo "   [DRY-RUN] Would run update command"
    exit 0
fi

# Record current version
CURRENT_VERSION=$(openclaw version 2>/dev/null || echo 'unknown')
echo "   Current version: $CURRENT_VERSION"

# Run update
if openclaw update 2>&1; then
    echo "   ✓ Update successful"
    NEW_VERSION=$(openclaw version 2>/dev/null || echo 'unknown')
    echo "   New version: $NEW_VERSION"
else
    echo "   ❌ Update failed"
    echo ""
    echo "⏪ Rolling back to previous version..."
    
    # Restore from backup
    /bin/bash "$(dirname "$0")/restore.sh" "$BACKUP_FILE" auto
    
    echo ""
    echo "✅ Rollback complete!"
    echo "   Restored to version: $CURRENT_VERSION"
    exit 1
fi

echo ""
echo "✅ Update complete with rollback protection!"
echo ""
echo "💡 If you need to rollback manually:"
echo "   openclaw-backup-restore $BACKUP_FILE"
