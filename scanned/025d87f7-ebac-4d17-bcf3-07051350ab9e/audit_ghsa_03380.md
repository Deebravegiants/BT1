# [H] OS Command Injection in im-metadata

## Summary
Severity: High
Advisory: GHSA-qfxv-qqvg-24pg
CVE: CVE-2019-10788
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-qfxv-qqvg-24pg
Type: github-advisory

## Affected
- npm: `im-metadata` — affected >=0

## Details
im-metadata through 3.0.1 allows remote attackers to execute arbitrary commands via the "exec" argument. It is possible to inject arbitrary commands as part of the metadata options which is given to the "exec" function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10788
- https://github.com/Turistforeningen/node-im-metadata/commit/ea15dddbe0f65694bfde36b78dd488e90f246639
- https://snyk.io/vuln/SNYK-JS-IMMETADATA-544184
