#!/bin/bash
#
# openclaw-restore.sh - Restore OpenClaw from a backup
#

set -e

BACKUP_FILE="$1"
RESTORE_MODE="${2:-ask}"  # ask, auto, or dry-run

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup-file.tar.gz> [ask|auto|dry-run]"
    echo ""
    echo "Modes:"
    echo "  ask     - Ask before overwriting each component (default)"
    echo "  auto    - Restore without prompting"
    echo "  dry-run - Show what would be restored without doing it"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Detect OpenClaw directories
OPENCLAW_DIR="${OPENCLAW_DIR:-$HOME/.openclaw}"
WORKSPACE_DIR="${WORKSPACE_DIR:-$OPENCLAW_DIR/workspace}"

# Create temp directory for extraction
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

echo "📦 Restoring OpenClaw from backup..."
echo "   Backup: $BACKUP_FILE"
echo ""

# Extract backup
echo "📂 Extracting backup..."
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"
BACKUP_NAME=$(ls "$TEMP_DIR" | head -1)
EXTRACTED_DIR="${TEMP_DIR}/${BACKUP_NAME}"

# Show backup info
if [ -f "${EXTRACTED_DIR}/backup-metadata.json" ]; then
    echo "📋 Backup Information:"
    cat "${EXTRACTED_DIR}/backup-metadata.json" | python3 -m json.tool 2>/dev/null || cat "${EXTRACTED_DIR}/backup-metadata.json"
    echo ""
fi

# Function to ask for confirmation
ask_confirm() {
    local component="$1"
    if [ "$RESTORE_MODE" = "auto" ]; then
        return 0
    elif [ "$RESTORE_MODE" = "dry-run" ]; then
        echo "   [DRY-RUN] Would restore: $component"
        return 1
    fi
    
    read -p "   Restore $component? (y/N): " response
    case "$response" in
        [Yy]*)
            return 0
            ;;
        *)
            echo "      ⏭ Skipped"
            return 1
            ;;
    esac
}

# Create pre-restore backup (rollback point)
if [ "$RESTORE_MODE" != "dry-run" ]; then
    echo "🔄 Creating pre-restore backup (rollback point)..."
    ROLLBACK_DIR="${OPENCLAW_DIR}-rollback-$(date +%Y%m%d_%H%M%S)"
    if [ -d "$OPENCLAW_DIR" ]; then
        cp -r "$OPENCLAW_DIR" "$ROLLBACK_DIR"
        echo "   ✓ Rollback point: $ROLLBACK_DIR"
    fi
    echo ""
fi

# Restore components
echo "📁 Restoring components:"

# 1. Config
if [ -d "${EXTRACTED_DIR}/openclaw-config" ]; then
    if ask_confirm "Configuration (~/.openclaw)"; then
        # Preserve current auth if it exists
        if [ -f "${OPENCLAW_DIR}/agents/main/agent/auth-profiles.json" ]; then
            cp "${OPENCLAW_DIR}/agents/main/agent/auth-profiles.json" "${EXTRACTED_DIR}/openclaw-config/agents/main/agent/auth-profiles.json" 2>/dev/null || true
        fi
        rm -rf "$OPENCLAW_DIR"
        cp -r "${EXTRACTED_DIR}/openclaw-config" "$OPENCLAW_DIR"
        echo "      ✓ Config restored"
    fi
fi

# 2. Workspace
if [ -d "${EXTRACTED_DIR}/workspace" ]; then
    if ask_confirm "Workspace"; then
        rm -rf "$WORKSPACE_DIR"
        cp -r "${EXTRACTED_DIR}/workspace" "$WORKSPACE_DIR"
        echo "      ✓ Workspace restored"
    fi
fi

# 3. Global skills (optional)
if [ -d "${EXTRACTED_DIR}/skills-global" ]; then
    if ask_confirm "Global Skills (requires sudo)"; then
        SKILLS_GLOBAL="/usr/lib/node_modules/openclaw/skills"
        sudo rm -rf "$SKILLS_GLOBAL"
        sudo cp -r "${EXTRACTED_DIR}/skills-global" "$SKILLS_GLOBAL"
        echo "      ✓ Global skills restored"
    fi
fi

if [ "$RESTORE_MODE" = "dry-run" ]; then
    echo ""
    echo "📝 Dry run complete. No changes were made."
else
    echo ""
    echo "✅ Restore complete!"
    echo ""
    echo "💡 If something went wrong, you can rollback:"
    echo "   cp -r ${ROLLBACK_DIR} ${OPENCLAW_DIR}"
fi
