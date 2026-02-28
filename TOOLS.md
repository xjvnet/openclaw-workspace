# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## Memory (LanceDB Pro)

### Jina AI Embedding
- API Key: jina_8b486f1b920244b3a0c2f395cb31f869dQTozoK12fX61Z7eis_jFCOYPfk0
- Model: jina-embeddings-v5
- Dimensions: 1024
- Task Query: retrieval.query
- Task Passage: retrieval.passage

### Memory Configuration
```json
{
  "memory-lancedb-pro": {
    "embedding": {
      "provider": "openai-compatible",
      "apiKey": "jina_8b486f1b920244b3a0c2f395cb31f869dQTozoK12fX61Z7eis_jFCOYPfk0",
      "model": "jina-embeddings-v5",
      "baseURL": "https://api.jina.ai/v1",
      "dimensions": 1024,
      "taskQuery": "retrieval.query",
      "taskPassage": "retrieval.passage",
      "normalized": true
    },
    "dbPath": "~/.openclaw/memory/lancedb",
    "autoCapture": true,
    "autoRecall": true
  }
}
```

Add whatever helps you do your job. This is your cheat sheet.
