# [M] VvvebJs Reflected Cross-Site Scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-pc95-3wgm-x28p
CVE: CVE-2024-29271
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-03-22
Source: https://github.com/advisories/GHSA-pc95-3wgm-x28p
Type: github-advisory

## Affected
- npm: `vvvebjs` — affected >=0 <1.7.5

## Details
A reflected Cross-Site Scripting (XSS) vulnerability in VvvebJs before version 1.7.5 allows remote attackers to execute arbitrary code and obtain sensitive information via the `action` parameter in `save.php`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29271
- https://github.com/givanz/VvvebJs/issues/342
- https://github.com/givanz/VvvebJs/commit/c0c0545b44b23acc288ef907fb498ce15b9b576e
- https://github.com/givanz/VvvebJs
