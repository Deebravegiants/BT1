# [M] Valine HTML Injection

## Summary
Severity: Medium
Advisory: GHSA-hhrp-qm88-xjr3
CVE: CVE-2018-19289
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-11-21
Source: https://github.com/advisories/GHSA-hhrp-qm88-xjr3
Type: github-advisory

## Affected
- npm: `valine` — affected >=0 <1.3.4

## Details
An issue was discovered in Valine v1.3.3. It allows HTML injection, which can be exploited for JavaScript execution via an EMBED element in conjunction with a .pdf file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19289
- https://github.com/xCss/Valine/issues/127
- https://github.com/xCss/Valine/commit/32d4d5e68df804f0eabb1a2bebbbf9459e31c2b7
- https://github.com/advisories/GHSA-hhrp-qm88-xjr3
- https://github.com/xCss/Valine
