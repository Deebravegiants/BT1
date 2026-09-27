# [H] MantisBT Vulnerable to Stored XSS in File Download

## Summary
Severity: High
Advisory: GHSA-p6fr-rxq7-xcg8
CVE: CVE-2026-44657
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:P/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-p6fr-rxq7-xcg8
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.28.2

## Details
Using *show_inline=1* parameter and a valid *file_show_inline_token* CSRF token on file_download.php, an attacker can execute code by uploading a crafted XHTML attachment referencing a JavaScript attachment.

### Impact
Cross-site scripting

### Patches
- 26647b2e68ba30b9d7987d4e03d7a16416684bc2

### Workarounds
None

### Credits
Thanks to siunam (Tang Cheuk Hei) for discovering and responsibly reporting the issue.

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-9c3j-xm6v-j7j3
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-p6fr-rxq7-xcg8
- https://nvd.nist.gov/vuln/detail/CVE-2026-44657
- https://github.com/mantisbt/mantisbt/commit/26647b2e68ba30b9d7987d4e03d7a16416684bc2
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=37020
