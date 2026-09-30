# [H] Improper neutralization of formula elements in yii-helpers

## Summary
Severity: High
Advisory: GHSA-f9p3-h6cg-2cjr
CVE: CVE-2022-1544
CWE: CWE-1236
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-03
Source: https://github.com/advisories/GHSA-f9p3-h6cg-2cjr
Type: github-advisory

## Affected
- Packagist: `luyadev/yii-helpers` — affected >=0 <1.2.1

## Details
Formula Injection/CSV Injection due to Improper Neutralization of Formula Elements in CSV File in GitHub repository luyadev/yii-helpers prior to 1.2.1. Successful exploitation can lead to impacts such as client-sided command injection, code execution, or remote ex-filtration of contained confidential data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1544
- https://github.com/luyadev/yii-helpers/commit/9956ed63f516110c2b588471507b870e748c4cfb
- https://github.com/luyadev/yii-helpers
- https://huntr.dev/bounties/fa6d6e75-bc7a-40f6-9bdd-2541318912d4
