<p align="center"><img src="docs/assets/hero-banner.png" alt="Word Safe Editing AI Agent Skill" width="100%"></p>

<p align="center"><strong>Edit existing Word documents with AI agents—more safely.</strong><br>
Backup, narrow edits, deterministic DOCX checks, Microsoft Word verification, and rollback.</p>

<p align="center">
<img alt="Experimental" src="https://img.shields.io/badge/status-experimental-f59e0b">
<img alt="Python standard library" src="https://img.shields.io/badge/Python-standard%20library-3776ab">
<img alt="macOS" src="https://img.shields.io/badge/platform-macOS-111827">
<img alt="MIT" src="https://img.shields.io/badge/license-MIT-22c55e">
</p>

<p align="center"><em>Reduces editing risk; it does not guarantee zero document damage.</em></p>

## 15-second visual tour

<p align="center"><img src="docs/assets/visual-walkthrough.gif" alt="Animated tour of the Word Safe Editing workflow" width="100%"></p>

## Why this skill exists

<p align="center"><img src="docs/assets/direct-vs-safe.png" alt="Unsafe direct AI editing compared with safety-first editing" width="100%"></p>

Direct AI editing can appear successful while damaging formatting, tables, images, or internal relationships. This skill adds recoverability and verification before delivery.

## The safety workflow

<p align="center"><img src="docs/assets/visual-workflow.svg" alt="Comparison and workflow diagram" width="100%"></p>

## Install in three steps

~~~bash
git clone https://github.com/ChrisZhangWG/word-safe-editing-ai-agent-skill.git
cp -R word-safe-editing-ai-agent-skill/skill/word-safe-editing ~/.codex/skills/
~~~

Restart Codex, then ask naturally:

~~~text
Please update the conclusion in this Word report without changing
its formatting, images, comments, or pagination.
~~~

Or explicitly invoke <code>$word-safe-editing</code>.

## What the agent does

1. Assesses the edit as Fast, Medium, or Full risk.
2. Creates a recoverable backup.
3. Makes the narrowest safe edit.
4. Validates ZIP, XML, relationships, and requested content boundaries.
5. Verifies the document opens and saves in Microsoft Word.
6. Delivers the result—or rolls back if verification fails.

## Three levels of protection

<p align="center"><img src="docs/assets/risk-tiers.png" alt="Fast, Medium, and Full Word editing risk tiers" width="100%"></p>

- **Fast:** small text-only changes with low layout risk.
- **Medium:** longer wording, page-edge content, highlights, or figure-adjacent text.
- **Full:** tables, images, captions, fields, page structure, formatting, or recent Word errors.

## Run the DOCX safety checker

~~~bash
python3 skill/word-safe-editing/scripts/check_docx_safety.py report.docx \\
  --must-contain "Revised conclusion" \\
  --must-not-contain "Old conclusion" \\
  --warn-unreferenced-media
~~~

The checker is read-only and uses only Python's standard library. A zero exit status means the selected structural checks passed; it does not replace visual QA or Word verification.

## Scope, privacy, and safety

Version 0.1 targets **Codex + macOS + Microsoft Word + existing DOCX files**. Legacy DOC, encrypted or protected documents, and macro-enabled files are not fully supported. Tests use only fictional temporary fixtures. Do not publish real private documents as examples.

## License

[MIT License](LICENSE) © 2026 Chris Zhang.
