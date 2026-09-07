# [H] Webrecorder packages are vulnerable to XSS through 404 error handling logic

## Summary
Severity: High
Advisory: GHSA-w765-jm6w-4hhj
CVE: CVE-2025-58765
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2025-09-10
Source: https://github.com/advisories/GHSA-w765-jm6w-4hhj
Type: github-advisory

## Affected
- npm: `@webrecorder/wabac` — affected >=0 <2.23.11
- npm: `replaywebpage` — affected >=0 <2.3.17
- npm: `@webrecorder/archivewebpage` — affected >=0 <0.15.4

## Details
A Reflected Cross-Site Scripting (XSS) vulnerability exists in the 404 error handling logic of wabac.js v2.23.10 and below. The parameter `requestURL` (derived from the original request target) is directly embedded into an inline `<script>` block without sanitization or escaping.

This allows an attacker to craft a malicious URL that executes arbitrary JavaScript in the victim’s browser.

The scope may be limited by CORS policies, depending on the situation in which wabac.js is used.

### Patches

The vulnerability is fixed in wabac.js v2.23.11.

## References
- https://github.com/webrecorder/wabac.js/security/advisories/GHSA-w765-jm6w-4hhj
- https://nvd.nist.gov/vuln/detail/CVE-2025-58765
- https://github.com/webrecorder/archiveweb.page/pull/315
- https://github.com/webrecorder/replayweb.page/pull/448
- https://github.com/webrecorder/wabac.js/commit/25feb4a5af69a6b65694426eae67b890be438c4c
- https://github.com/webrecorder/replayweb.page/releases/tag/v2.3.17
- https://github.com/webrecorder/wabac.js
- https://github.com/webrecorder/wabac.js/releases/tag/v2.23.11
