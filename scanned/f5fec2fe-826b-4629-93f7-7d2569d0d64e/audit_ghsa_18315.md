# [M] Decap CMS Cross Site Scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-xp8g-32qh-mv28
CVE: CVE-2025-57520
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-09-10
Source: https://github.com/advisories/GHSA-xp8g-32qh-mv28
Type: github-advisory

## Affected
- npm: `decap-cms` — affected >=0

## Details
Decap CMS through 3.8.3 is vulnerable to stored Cross-Site Scripting (XSS) in the admin preview pane. User-controlled fields (e.g., title, description, tags, and body) are rendered in the preview without sufficient sanitization/escaping. An attacker with low-privilege author/contributor access can persist a JavaScript payload in content; when a maintainer or reviewer opens the preview, the payload executes in the CMS admin origin, enabling token/session theft or the execution of privileged actions via the DOM. The issue affects multiple input vectors and requires only passive interaction from the previewing user. As no patched version is available, administrators should restrict untrusted contributor roles and filter or disable preview rendering of untrusted HTML.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-57520
- https://github.com/decaporg/decap-cms
- https://onurcangenc.com.tr/posts/cve-2025-57520--stored-xss-in-decap-cms-3-8-3
