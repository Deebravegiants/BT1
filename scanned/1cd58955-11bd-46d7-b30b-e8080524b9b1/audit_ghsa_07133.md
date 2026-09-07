# [C] SiYuan: Stored XSS to RCE via Unsanitized Attribute View Asset Cell Content

## Summary
Severity: Critical
Advisory: GHSA-56mp-4f3v-fgj2
CVE: CVE-2026-50551
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-10
Source: https://github.com/advisories/GHSA-56mp-4f3v-fgj2
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260628153353-2d5d72223df4

## Details
SiYuan v3.6.5 and earlier versions contain a stored cross-site scripting (XSS) vulnerability in the Attribute View (database) asset cell renderer that escalates to remote code execution (RCE) in the Electron desktop client. This is a neighbor-bug of CVE-2026-44588: the fix for -44588 used `escapeAriaLabel()` (double-escapes `<`), but the AV asset renderers were left using the weaker `escapeAttr()` (escapes only quotes) or no escaping at all.

  ## Vulnerability Details

  The Electron renderer is configured with `nodeIntegration: true` and `contextIsolation: false` (app/electron/main.js:307), allowing any JavaScript executing in the renderer to directly access Node.js APIs including `require('child_process')`.

  Two XSS sinks exist.

  ### Sink 1 (Direct Stored XSS - triggers on page load)

  `app/src/protyle/render/av/cell.ts:1008`:

      text += `<span class="b3-chip av__celltext--url ariaLabel" aria-label="${escapeAttr(item.content)}" data-name="${escapeAttr(item.name)}"
  data-url="${escapeAttr(item.content)}">${item.name || item.content}</span>`;

  The `>${item.name || item.content}</span>` portion is raw user input with zero escaping.

  `app/src/protyle/render/av/blockAttr.ts:93` (even worse - completely unescaped):

      html += `<img loading="lazy" class="av__cellassetimg ariaLabel" aria-label="${item.content}" src="${getCompressURL(item.content)}">`;

  Rendered via `action.ts:860`: `cellElement.innerHTML = renderCell(...)` results in immediate XSS on page load.

  ### Sink 2 (Hover-triggered XSS via aria-label round-trip)

  - Same lines emit `aria-label="${escapeAttr(item.content)}"` on `.ariaLabel` elements.
  - `escapeAttr()` (util/escape.ts:14) escapes only `"` and `'` — NOT `<` or `>`.
  - `popover.ts:33` global mouseover handler reads `aria-label` via `getAttribute` (which attribute-decodes entities).
  - Line 144: `showTooltip(decodeURIComponent(tip), ...)` then `tooltip.ts:41`: `messageElement.innerHTML = message` results in XSS on hover.

  ### Source

  - `app/src/protyle/render/av/asset.ts:405`: `addAssetLink()` reads user input from a free-form `<textarea>` with no sanitization.
  - Kernel stores `MAsset.Content` raw (kernel/av/value.go:53), no server-side sanitization.

  ## Attack Vector

  1. Attacker creates a malicious note containing an Attribute View (database).
  2. Attacker adds an asset cell with link content: `<img src=x onerror=require('child_process').exec('calc')>`
  3. Victim opens the note for immediate RCE (Sink 1), or hovers over the cell for RCE (Sink 2).
  4. In a sync/collaboration scenario, the malicious note propagates to all users.

  ## Proof of Concept

  Payload (Direct XSS) — in an AV asset cell link field, enter:

      <img src=x onerror=alert(document.domain)>

  For RCE in Electron desktop:

      <img src=x onerror=require('child_process').exec('calc')>

  ### Steps to Reproduce

  1. Open SiYuan desktop app (v3.6.5).
  2. Create a new document.
  3. Insert an Attribute View (database): `/` then select "Table".
  4. Add a column of type "Asset".
  5. Click the asset cell, then "Add Link".
  6. In the "Link" textarea, paste: `<img src=x onerror=alert(1)>`
  7. Leave "Title" empty or fill with benign text.
  8. Click outside the dialog to save.
  9. Observe: Alert fires immediately (Sink 1). Hovering over the cell also triggers (Sink 2).

  ## Impact

  - Remote Code Execution on victim's system via malicious note sync/import.
  - Data exfiltration: attacker can read all notes, access filesystem, steal credentials.
  - Persistence: malicious payload stored in `.sy` files, executes on every open.

  ## Suggested Fix

  1. Replace `escapeAttr()` with `escapeAriaLabel()` for all `aria-label` attributes in AV cell renderers.
  2. Escape `item.name` and `item.content` with `escapeHtml()` before concatenating into element text content.

  Affected files: `app/src/protyle/render/av/cell.ts`, `app/src/protyle/render/av/blockAttr.ts`, `app/src/protyle/render/av/asset.ts`.

  ## Additional Context

  This vulnerability is a neighbor-bug of CVE-2026-44588. The fix for -44588 correctly used `escapeAriaLabel()` (which double-escapes `<` to survive the attribute -> `getAttribute` -> `innerHTML` round-trip), but the AV asset cell renderers were left using the weaker `escapeAttr()` or no escaping. This is part of a pattern of incomplete fixes in SiYuan (see also CVE-2026-33066, CVE-2026-29183). The long-term fix should set Electron`contextIsolation: true` and `nodeIntegration: false`.

  ## Report
 Reporter (GitHub: Yunkaiwjs).

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-56mp-4f3v-fgj2
- https://nvd.nist.gov/vuln/detail/CVE-2026-50551
- https://github.com/siyuan-note/siyuan
