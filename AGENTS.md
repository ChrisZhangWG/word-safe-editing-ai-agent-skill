# Project Agent Notes

## README And Visual Explanation Preferences

- This project is for AI agents, so public-facing instructions should be agent-first. Prefer prompts such as "ask your AI agent to install/run/check this" before command-line snippets. Keep command-line usage as a technical fallback.
- README visuals should be explanation-driven, not merely decorative. Each figure should answer a specific reader question, such as why DOCX editing is risky, what the skill changes, how the safety tier is chosen, what the checker can prove, or how a worked example flows.
- When creating educational, workflow, infographic, sketchnote, whiteboard, or concept-memory figures for this project, use `/Users/chris/.codex/skills/visual-gem-picture/SKILL.md` first. Do not default to rough hand-written SVG diagrams for public README figures unless the user explicitly asks for deterministic/editable SVG output.
- For AI-generated figures, keep labels short and validate visible text before using them in the README. Reject or regenerate figures with malformed labels, nonsense words, overlapping text, or visuals that look good but do not explain the concept.
- For formal editable diagrams, follow the Visual Gem workflow first: generate an AI image draft, validate it, then redraw semantically as editable SVG only if exact text or editability matters.

## Publishing Hygiene

- Before publishing README or asset changes, check the rendered references, run the existing DOCX checker tests, and remove temporary generated files that are not part of the final project.
