---
name: word-safe-editing
description: "Safely and efficiently edit existing Word/DOCX files when preserving document structure matters. Use for existing .docx files, reviewed Word reports, template-based reports, OneDrive/SharePoint Word files, files with images, captions, fields, numbering, tables, comments, highlights, tracked changes, or any case involving Word unreadable-content alerts, save failures, formatting corruption risk, or requests to modify a Word file without breaking layout. Choose the lightest safe path: fast checks for narrow text-only edits, medium checks for wording that may affect layout, and full Word/render/Word-open verification for images, captions, tables, fields, page breaks, formatting, or recent open/save failures. For template-based reports, copy the source/template document and edit that copy; do not rebuild, imitate, convert, or re-export when the goal is preserving the original layout."
---

# Word Safe Editing

## Purpose

Use this skill when editing an existing Word/DOCX file is riskier than creating a new document. The priority is preserving the original document structure and leaving the user with a file that opens and saves in Microsoft Word without repair, unreadable-content, or save-failure alerts.

For brand-new document deliverables, use the Documents skill/plugin. For existing reviewed reports, template-based reports, OneDrive/SharePoint Word files, or files with captions, images, fields, comments, highlights, tables, numbering, or careful layout, follow this skill first.

## Hard Rules

- Do not rebuild or re-export the whole document unless the user explicitly wants a new copy.
- For template-based or reviewed reports, begin from an exact copy of the original/template DOCX and modify only the requested content.
- Do not use LibreOffice, Pandoc, Word recovery, or other conversion/save-as paths as a layout-preserving repair/edit method unless the user explicitly accepts formatting drift.
- Do not directly patch `.docx` internal XML as the first choice when Microsoft Word can perform the edit safely.
- If XML/OOXML editing is necessary, keep it narrow, preserve namespaces and relationships, and verify the result in Microsoft Word.
- Do not treat `unzip -t`, XML well-formed checks, or rendered previews as sufficient proof that Word accepts the file.
- Do not leave extra working copies, scratch files, rendered previews, or backup files in the user's project folder unless needed or explicitly requested.
- Keep Codex-only backups, scratch files, and rendered previews in a temporary or other non-project location when practical, but do not ask Microsoft Word to open, save, or export to arbitrary `/tmp` or random temporary paths. Use the target DOCX or a stable, already-authorized staging path for Word-native operations.
- Do not delete, restore, or replace images globally through `word/media`; scope image changes by section, relationship, drawing element, table cell, or explicit user instruction.
- When deleting images or figure blocks inside tables, check for leftover fixed row heights, empty placeholder rows, broken picture boxes, and stale captions.
- Preserve non-target highlights, comments, tracked changes, local formatting, fields, bookmarks, hyperlinks, numbering, tables, images, captions, headers, footers, and page layout.

## Risk Tier Selection

Use the lightest workflow that is defensible for the requested change. Do not run the full render-and-repair workflow by default for every minor wording edit.

Start read-only for review, source comparison, typo identification, or QA requests. Switch to an editing workflow only after the user asks to modify the document or approves a specific edit.

### Fast Path: narrow text-only edits

Use this when all of the following are true:

- The user asks for a small wording replacement, typo fix, or sentence/paragraph text change.
- The edit does not touch images, captions, fields, cross-references, tables, numbering, page breaks, headers/footers, comments, tracked changes, styles, or manual highlighting.
- The replacement text is similar enough in length that pagination/layout risk is low.
- The file has not shown Word unreadable-content or save-failure alerts during the current work session.

Fast-path checks:

1. Confirm the target file exists and make a temporary backup outside the project folder.
2. Prefer Word automation for the edit when feasible; otherwise make the narrowest possible OOXML change without altering paragraph/run properties.
3. Verify the changed text and confirm expected non-target highlight/comment counts where relevant.
4. Run basic DOCX integrity checks: zip validity, edited XML well-formedness, and no missing `mc:Ignorable` namespace declarations if XML was touched.
5. Open and save in Microsoft Word if the document is on OneDrive/SharePoint, is currently open in Word, or the edit was made through OOXML. If the edit was made directly in Word and saved without alerts, this gate is already satisfied.
6. Skip visual rendering unless text length, page position, or user concern makes layout drift plausible.
7. Remove the temporary backup after final verification unless the user asks to keep it.

### Medium Path: wording with layout risk

Use this when the edit is still mostly text but may affect visible layout, for example longer paragraph rewrites, text near page bottoms, section headings, figure-adjacent paragraphs, highlighted review text, or repeated replacements.

Medium-path checks:

1. Follow the Fast Path.
2. Compare the affected paragraph/run properties before and after when manual formatting matters.
3. Render only the affected page and nearby page when practical, or use Word visual inspection if rendering would cost more than it saves.
4. Check that pagination, adjacent figures/captions, table borders, and highlights remain acceptable.

### Full Path: structure, formatting, figures, or recent Word errors

Use the full workflow below when any of these apply:

- Images, captions, `SEQ Figure` / `SEQ Table` fields, cross-references, tables, numbering, page breaks, section breaks, headers/footers, comments, tracked changes, styles, or cloned formatting are edited.
- The user explicitly asks to match formatting, preserve exact layout, insert captions through Word-like behavior, or start content on a new page.
- The file is a reviewed/report deliverable where the edit can change pagination or visual presentation.
- Word has recently shown unreadable-content, repair/recovery, conversion, or could-not-save alerts for the file.
- OOXML editing changes relationships, media files, drawing IDs, fields, table structure, or namespace declarations.

Full-path checks:

1. Follow the complete Safe Workflow below.
2. Render affected pages plus surrounding pages.
3. Perform both Word-open and Word-save gates even if non-Word renderers accept the file.
4. Re-check key invariants after Word saves, because Word may normalize fields, image metadata, and XML.

## Safe Workflow

1. Confirm the target path and live file state.
   - Verify the file exists.
   - Check whether it is on OneDrive/SharePoint or already open in Word.
   - If project instructions exist, read them before modifying project files.
   - Save and close the target document in Word before file-level edits when feasible.

2. Make one recoverable backup before modifying.
   - Prefer a local temporary backup outside the user's project folder when possible.
   - For template-based report generation, copy the exact source/template DOCX first and edit the copy; do not create a fresh DOCX that tries to mimic the template.
   - If a project-folder backup is needed during repair, give it a clear temporary name and remove it after verification unless the user asks to keep it.
   - If the edit fails, Word reports unreadable content, or Word cannot save, restore or rebuild from the last known-good backup.

3. Choose the lowest-risk edit path.
   - Preferred for existing complex Word files: open the document in Microsoft Word and let Word make/save the change.
   - Use Word automation, AppleScript, or UI control when it can perform the edit without damaging formatting.
   - Use OOXML patching only for narrow changes that Word automation cannot reliably perform, such as precise field/caption or cloned-format edits.

4. Keep edits narrow.
   - Modify only requested paragraphs, runs, cells, rows, captions, images, fields, page breaks, or section elements.
   - If exact matching to another part/template is required, clone the target element's OOXML and replace only the necessary text/content.
   - Do not guess from style names alone. Compare paragraph properties, run properties, numbering, table geometry, drawing geometry, and field structure where relevant.

5. Preserve Word-native captions and fields.
   - When the user expects References > Insert Caption behavior, create or preserve native `SEQ Figure` / `SEQ Table` fields.
   - Accept both Word field forms: complex fields using `w:instrText` and simple fields using `w:fldSimple`.
   - Preserve visible caption text, `Caption` style, numbering, cross-reference compatibility, and Table of Figures compatibility.

6. Run structural checks before visual review.
   - Check the DOCX zip container.
   - Check edited XML is well formed.
   - Check relationships, media references, duplicate drawing IDs, caption fields, table-cell closure, and expected paragraph/image counts when relevant.
   - If `mc:Ignorable` lists namespace prefixes, confirm those prefixes are declared on the same XML root. Missing namespace declarations can make Word report unreadable content even when other renderers open the file.
   - Run `scripts/check_docx_safety.py` for any OOXML edit, image/table edit, field edit, or document that recently failed to open/save in Word. Add project-specific `--must-contain`, `--must-not-contain`, `--forbid-images-between`, and row-height checks when the user has defined content boundaries.
   - On macOS/OneDrive files, check writable permissions and remove `com.apple.quarantine` when it interferes with Word opening/saving.

7. Render and visually review.
   - Use the Documents skill render workflow for DOCX QA.
   - Keep renderer inputs and outputs in Codex-controlled temporary storage; do not route ordinary visual QA through a fresh Word export in `/tmp`.
   - Inspect affected pages plus surrounding pages.
   - Check for changed pagination, pushed figures, orphaned captions, broken table borders, clipping, overlap, blank pages, broken-picture placeholders, oversized blank table boxes, and text that no longer fits.

8. Perform the Word-open gate.
   - Open the final file in Microsoft Word.
   - Open the target DOCX through the normal user-facing file path or an already-open document; do not use Word automation to open a newly generated temporary file unless its path is stable and authorized.
   - Confirm Word does not show unreadable-content, repair, recover-content, or conversion alerts.
   - If Word shows an alert, do not proceed as if the document is good. Diagnose and fix the file, or restore from backup and reapply the change through Word.

9. Perform the Word-save gate.
   - Save the file in Microsoft Word or make a Word-saved clean copy and replace the target only after verification.
   - If Word-native PDF export is required for a layout-sensitive check, reuse one stable authorized destination or save to the user's explicitly requested final location; do not generate a new random temporary export path for each run.
   - Confirm Word does not show "could not be saved" or any save-failure alert.
   - Re-check key invariants after Word saves, because Word may normalize field representation, image metadata, or XML structure.
   - If Word converts complex `SEQ Figure` fields into `fldSimple` `SEQ Figure` fields, treat that as acceptable Word-native field preservation.

10. Clean up.
   - Remove temporary scripts, scratch folders, rendered previews, logs, test copies, and unnecessary backups.
   - Leave only the intended edited document and any files the user explicitly asked to keep.

## Template-Based Reports and Image/Table Edits

Use this section whenever a report must keep the formatting of a previous Word template.

1. Identify the source/template DOCX and copy it byte-for-byte to the target output path before editing.
2. Replace only target text, figures, table rows, captions, and sections. Keep existing styles, page setup, headers, footers, fields, numbering, margins, and table geometry unless the user asks to change them.
3. If a section must exclude observations, suggestions, categories, or figures, remove only the matching section content. Do not restore old template figures or captions into the new report.
4. When deleting image rows or category sections inside tables, remove the drawing/caption row and then verify the surrounding table row heights. A removed image can leave a large fixed-height blank row that renderers may not flag as an error.
5. Run a boundary check with `scripts/check_docx_safety.py` before final Word-open/save gates, for example:

   ```bash
   python3 ${CODEX_HOME:-$HOME/.codex}/skills/word-safe-editing/scripts/check_docx_safety.py \
     "/path/to/report.docx" \
     --must-not-contain "forbidden old-template text" \
     --forbid-images-between "Section Start" "Next Section" \
     --forbid-figure-captions-between "Section Start" "Next Section" \
     --max-row-height-between "Section Start" "Next Section" 3000
   ```

## When Word Shows "Unreadable Content"

If Word says it found unreadable content:

1. Stop editing that file in Word.
2. Do not click recovery unless the user explicitly wants Word's recovered version.
3. Preserve the problematic file only long enough to diagnose.
4. Check XML well-formedness, zip integrity, root namespace declarations, `mc:Ignorable`, relationships, drawing IDs, image references, caption fields, and table structure.
5. Restore from a known-good copy or create a Word-saved clean copy after the root cause is fixed.
6. Reopen in Word and verify no unreadable-content alert appears.

## When Word Cannot Save

If Word says the document could not be saved:

1. Stop making further edits in that Word window.
2. Check file permissions, OneDrive/SharePoint state, locks, quarantine attributes, and whether the file is still writable.
3. Use Word's own Save As to create a clean copy when possible.
4. Verify the clean copy opens and saves in Word.
5. Replace the target only after the clean copy passes structural checks, render review, Word-open gate, and Word-save gate.
6. Remove temporary repair backups after the user confirms the final file works.

## Validation Checklist

Before finalizing, confirm the checks required by the selected risk tier:

- The document opens in Microsoft Word without unreadable-content, repair, recover-content, or conversion alerts.
- The document saves in Microsoft Word without save-failure alerts.
- The requested content or layout change is present.
- The document was edited from the correct original/template when template fidelity matters.
- No forbidden old-template text remains when replacement/removal was requested.
- Non-target highlights, comments, tracked changes, tables, images, captions, fields, numbering, headers/footers, and important formatting are preserved.
- Captions remain Word-native fields when required.
- No unwanted images, figure captions, broken-picture placeholders, or oversized blank table rows remain in sections where the user asked to remove them.
- Rendered affected pages are visually clean when the Medium Path or Full Path requires rendering.
- No unnecessary temporary files or duplicate backups remain in the user's project folder.

For a Fast Path edit made directly through Microsoft Word and saved without alerts, do not spend extra time rendering unless there is a concrete layout risk. State the lighter verification used in the final response.

