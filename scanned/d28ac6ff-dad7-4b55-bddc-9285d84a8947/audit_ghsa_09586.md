# [M] Kimai has Stored XSS via Incomplete HTML Attribute Escaping in Team Member Widget

## Summary
Severity: Medium
Advisory: GHSA-g82g-m9vx-vhjg
CVE: CVE-2026-40479
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-15
Source: https://github.com/advisories/GHSA-g82g-m9vx-vhjg
Type: github-advisory

## Affected
- Packagist: `kimai/kimai` — affected >=0 <2.53.0

## Details
### Summary
The client-side `escapeForHtml()` function in `KimaiEscape.js`, introduced in commit `89bfa82c` (#2959) to fix a JavaScript XSS vulnerability, only escapes `<`, `>`, and `&` but does not escape `"` (double quote) or `'` (single quote). When user-controlled data (profile alias) is placed in an HTML attribute context (`title="__DISPLAY__"`) via the team member form prototype and rendered through `innerHTML`, the missing quote escaping allows HTML attribute injection, resulting in Stored XSS.

### Details
Incomplete security patch. The `escapeForHtml()` function was meant to prevent XSS but missed quote characters, which are critical for HTML attribute context escaping.

**Vulnerable code** — `assets/js/plugins/KimaiEscape.js:29-33`:
```javascript
const tagsToReplace = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    // MISSING: '"': '&quot;'
    // MISSING: "'": '&#039;'
};
```

**Affected code files**:
- `assets/js/plugins/KimaiEscape.js:24-38` — incomplete escape function
- `assets/js/forms/KimaiTeamForm.js:77,86` — replacement + innerHTML
- `templates/macros/widgets.html.twig:126` — `title="{{ tooltip }}"` in avatar macro
- `templates/form/blocks.html.twig:104` — `{{ widgets.avatar('__INITIALS__', '__COLOR__', '__DISPLAY__') }}`

### PoC
[poc.zip](https://github.com/user-attachments/files/26537515/poc.zip)

Please extract the uploaded compressed file before proceeding

1. ./setup.sh
2. ./poc_xss.sh

<img width="751" height="155" alt="스크린샷 2026-04-07 오후 9 06 27" src="https://github.com/user-attachments/assets/c09a23fb-f60b-49dd-9018-8c723e35b4c4" />

### Impact
- Stored XSS: payload persists in the database (user alias field)
- Privilege escalation: ROLE_USER injects XSS that executes in ROLE_ADMIN/ROLE_SUPER_ADMIN browser session

## References
- https://github.com/kimai/kimai/security/advisories/GHSA-g82g-m9vx-vhjg
- https://nvd.nist.gov/vuln/detail/CVE-2026-40479
- https://github.com/kimai/kimai/pull/2959
- https://github.com/kimai/kimai
- https://github.com/kimai/kimai/releases/tag/2.53.0
