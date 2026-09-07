# [M] MantisBT has Potential Referer-Based Reflected HTML Injection / XSS in Tag Update Page

## Summary
Severity: Medium
Advisory: GHSA-6jh4-47v2-4g37
CVE: CVE-2026-40598
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-6jh4-47v2-4g37
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.28.2

## Details
Improper escaping of the redirection page (retrieved from the request's *Referer* header) allows an attacker to inject HTML.

While this is generally not directly actionable as modern browsers will URL-encode special characters, on some specific server configurations this could poison the cache, leading to cross-site scripting.

### Impact
Cross-site scripting (XSS).

### Patches
- b1ebc57763f104eb5f541b7b4d1ce6948168abd9

### Workarounds
None

### Credits
Thanks to siunam (Tang Cheuk Hei) for discovering and responsibly reporting the issue.

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-6jh4-47v2-4g37
- https://nvd.nist.gov/vuln/detail/CVE-2026-40598
- https://github.com/mantisbt/mantisbt/commit/b1ebc57763f104eb5f541b7b4d1ce6948168abd9
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=37017
