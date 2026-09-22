# [M] EC-CUBE Improper Restriction of Rendered UI Layers or Frames

## Summary
Severity: Medium
Advisory: GHSA-rwh8-h525-4jvj
CVE: CVE-2020-5679
CWE: CWE-1021
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rwh8-h525-4jvj
Type: github-advisory

## Affected
- Packagist: `ec-cube/ec-cube` — affected >=3.0.0

## Details
Improper restriction of rendered UI layers or frames in EC-CUBE versions from 3.0.0 to 3.0.18 leads to clickjacking attacks. If a user accesses a specially crafted page while logged into the administrative page, unintended operations may be conducted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-5679
- https://github.com/EC-CUBE/ec-cube
- https://jvn.jp/en/jp/JVN24457594/index.html
- https://www.ec-cube.net/info/weakness
