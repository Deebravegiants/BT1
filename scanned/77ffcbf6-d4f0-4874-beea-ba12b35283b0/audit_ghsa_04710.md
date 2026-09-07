# [H] @angular/platform-server: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')

## Summary
Severity: High
Advisory: GHSA-hqr9-c56f-3x7f
CVE: CVE-2026-50555
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-hqr9-c56f-3x7f
Type: github-advisory

## Affected
- npm: `@angular/platform-server` — affected >=22.0.0-next.0 <22.0.0-rc.2
- npm: `@angular/platform-server` — affected >=21.0.0-next.0 <21.2.16
- npm: `@angular/platform-server` — affected >=20.0.0-next.0 <20.3.24
- npm: `@angular/platform-server` — affected >=19.0.0-next.0 <19.2.25
- npm: `@angular/platform-server` — affected >=0

## Details
A Cross-Site Scripting (XSS) vulnerability exists in `@angular/platform-server`'s DOM emulation dependency (`domino`) when serializing the content of raw-text elements (such as `<script>`, `<style>`, and `<iframe>`).

`domino` supports escaping raw-text elements during serialization to prevent closing-tag breakout. However, a **Unicode index alignment bug** existed in this escaping logic.

In JavaScript, string lengths and character indices are calculated based on UTF-16 code units (where astral characters—such as emojis—occupy 2 code units / 4 bytes). If the bound dynamic text contained astral Unicode characters _before_ the closing tag (e.g. `</script>`, `</style>`, or `</iframe>`), the index offset calculation in `domino`'s replacement logic shifted.

This misalignment caused `domino` to fail to replace or escape the closing tag, leaving it raw and unescaped in the output HTML.

An attacker who controls the dynamic text can supply a payload containing both an astral Unicode character and a closing tag (e.g., `😀</iframe><script>alert(1)</script>`). When serialized on the server during SSR, the browser parses the unescaped closing tag, exits the raw-text context early, and executes the subsequent `<script>` block, leading to same-origin Cross-Site Scripting (XSS).

### Impact

This vulnerability allows an attacker to perform same-origin Cross-Site Scripting (XSS) attacks against any user visiting an SSR-rendered page that binds user-controlled data inside raw-text elements. This can lead to session hijacking, credentials theft, unauthorized actions on behalf of users, and defacement.

### Patched Versions

- 22.0.0-rc.2
- 21.2.16
- 20.3.24
- 19.2.25

### Workarounds

If you cannot immediately update your dependencies, you can:

- Avoid binding user-controlled values inside `<iframe>` or other raw-text elements.
- Sanitize any user input placed inside raw-text elements to explicitly strip closing tags before passing it to the template.

## References
- https://github.com/angular/angular/security/advisories/GHSA-hqr9-c56f-3x7f
- https://nvd.nist.gov/vuln/detail/CVE-2026-50555
- https://github.com/angular/domino/pull/29
- https://github.com/angular/angular
