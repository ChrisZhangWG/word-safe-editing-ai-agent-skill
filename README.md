# Word Safe Editing AI Agent Skill

A safety-first Codex skill and deterministic DOCX validation tool for AI agents editing existing Microsoft Word documents.

> [!IMPORTANT]
> This project reduces editing risk; it cannot guarantee that a Word document will never be damaged. Backups, structural checks, visual review, Microsoft Word open/save gates, and rollback remain essential.

## Scope

The experimental v0.1 release targets Codex on macOS with Microsoft Word and existing `.docx` files. Legacy `.doc`, encrypted or protected documents, and macro-enabled files are not fully supported.

## Install

```bash
git clone https://github.com/ChrisZhangWG/word-safe-editing-ai-agent-skill.git
cp -R word-safe-editing-ai-agent-skill/skill/word-safe-editing ~/.codex/skills/
```

Restart Codex, then ask naturally or invoke the skill explicitly:

```text
Use $word-safe-editing to revise this existing Word report while preserving its formatting, images, comments, and pagination.
```

## DOCX safety checker

The checker is read-only and uses only Python's standard library:

```bash
python3 skill/word-safe-editing/scripts/check_docx_safety.py report.docx \
  --must-contain "Revised conclusion" \
  --must-not-contain "Old conclusion" \
  --warn-unreferenced-media
```

A zero exit status means the selected structural checks passed. It does not replace visual QA or verification in Microsoft Word.

## Privacy

The repository contains only synthetic test documents. Do not publish real client, employer, research, or personal documents as fixtures.

## Project status

Experimental. Automated tests and installation validation are required before v0.1.0 publication.

## License

MIT License. See [LICENSE](LICENSE).
