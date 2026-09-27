# [M] VvvebJs Arbitrary File Upload vulnerability

## Summary
Severity: Medium
Advisory: GHSA-pmm3-68q9-57jg
CVE: CVE-2024-29272
CWE: CWE-434
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-03-22
Source: https://github.com/advisories/GHSA-pmm3-68q9-57jg
Type: github-advisory

## Affected
- npm: `vvvebJs` — affected >=0 <1.7.5

## Details
Arbitrary File Upload vulnerability in VvvebJs before version 1.7.5, allows unauthenticated remote attackers to execute arbitrary code and obtain sensitive information via the sanitizeFileName parameter in save.php.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29272
- https://github.com/givanz/VvvebJs/issues/343
- https://github.com/givanz/VvvebJs/commit/c6422cfd4d835c2fa6d512645e30015f24538ef0
- https://github.com/givanz/VvvebJs
