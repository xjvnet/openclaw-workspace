---
name: openclaw-backup
description: OpenClaw complete backup, restore, and update with automatic rollback support. Use when backing up OpenClaw configuration, workspace, and skills; restoring from backup; updating OpenClaw with rollback protection; or managing OpenClaw disaster recovery.
---

# OpenClaw Backup

Complete backup, restore, and update management for OpenClaw with automatic rollback support.

## What This Skill Does

- **Backup**: Save OpenClaw configuration, workspace, and custom skills
- **Restore**: Recover from backups with interactive or automatic modes
- **Update**: Update OpenClaw with automatic rollback on failure
- **Rollback**: Automatic and manual rollback to previous states

## Quick Start

### Backup Everything

```bash
# Default backup location (~/openclaw-backups)
./scripts/backup.sh

# Custom backup directory
./scripts/backup.sh /path/to/backups
```

### Restore from Backup

```bash
# Interactive restore (asks before overwriting)
./scripts/restore.sh /path/to/backup.tar.gz

# Automatic restore (no prompts)
./scripts/restore.sh /path/to/backup.tar.gz auto

# Dry run (see what would be restored)
./scripts/restore.sh /path/to/backup.tar.gz dry-run
```

### Update with Rollback Protection

```bash
# Update with automatic rollback on failure
./scripts/update.sh

# Dry run (see what would happen)
./scripts/update.sh --dry-run
```

## What's Backed Up

| Component | Location | Notes |
|-----------|----------|-------|
| Configuration | `~/.openclaw/` | Main config, agents, auth |
| Workspace | `~/.openclaw/workspace/` | Your projects and data |
| Custom Skills | `~/.openclaw/workspace/skills/` | Your custom skills |
| Global Skills | `/usr/lib/node_modules/openclaw/skills/` | Optional (may need sudo) |

## Backup Structure

```
openclaw-backup-YYYYMMDD_HHMMSS/
├── backup-metadata.json    # Backup info (date, version, etc.)
├── openclaw-config/        # ~/.openclaw contents
├── workspace/              # Workspace files
└── skills-global/          # Global skills (if backed up)
```

## Rollback Behavior

### Update Rollback

When running `./scripts/update.sh`:

1. Pre-update backup is created automatically
2. Update is attempted
3. If update fails → **automatic rollback** to previous state
4. If update succeeds → backup kept for manual rollback if needed

### Manual Rollback

If you need to rollback after a successful update:

```bash
# Find your pre-update backup
ls -la ~/openclaw-backups/pre-update-*.tar.gz

# Restore it
./scripts/restore.sh ~/openclaw-backups/pre-update-XXXX.tar.gz auto
```

## Scripts Reference

### backup.sh

```bash
./scripts/backup.sh [backup-directory]
```

Creates a timestamped backup archive.

### restore.sh

```bash
./scripts/restore.sh <backup-file.tar.gz> [mode]
```

Modes:
- `ask` (default) - Prompt before overwriting each component
- `auto` - Restore without prompts
- `dry-run` - Show what would be restored without making changes

### update.sh

```bash
./scripts/update.sh [--dry-run]
```

Updates OpenClaw with automatic rollback protection.

## Best Practices

1. **Backup before major changes** - Always backup before updating or making significant config changes
2. **Keep multiple backups** - Old backups are not deleted automatically
3. **Test restores** - Periodically verify backups work with `dry-run` mode
4. **Store backups offsite** - Copy important backups to external storage

## Troubleshooting

### Permission Denied on Global Skills

Global skills require elevated permissions. Either:
- Skip global skills backup (custom skills in workspace are usually sufficient)
- Run backup with `sudo` (not recommended - may create permission issues)

### Backup Too Large

Consider excluding:
- Large model caches (usually in `~/.openclaw/cache/`)
- Node modules in workspace projects
- Log files

Edit `scripts/backup.sh` and add `--exclude` patterns to the `cp -r` commands.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENCLAW_DIR` | `~/.openclaw` | OpenClaw configuration directory |
| `WORKSPACE_DIR` | `~/.openclaw/workspace` | Workspace directory |
| `SKILLS_GLOBAL` | `/usr/lib/node_modules/openclaw/skills` | Global skills directory |
