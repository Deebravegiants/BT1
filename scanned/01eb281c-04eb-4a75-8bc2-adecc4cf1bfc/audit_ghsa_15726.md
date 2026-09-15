# [H] node-twain vulnerable to Improper Check or Handling of Exceptional Conditions

## Summary
Severity: High
Advisory: GHSA-wxr3-2hgv-qm8f
CVE: CVE-2024-21525
CWE: CWE-703
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2024-07-10
Source: https://github.com/advisories/GHSA-wxr3-2hgv-qm8f
Type: github-advisory

## Affected
- npm: `node-twain` — affected >=0

## Details
All versions of the package node-twain are vulnerable to Improper Check or Handling of Exceptional Conditions due to the length of the source data not being checked. Creating a new twain.TwainSDK with a productName or productFamily, manufacturer, version.info property of length >= 34 chars leads to a buffer overflow vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21525
- https://gist.github.com/dellalibera/55b87634a6c360e5be22a715f0566c99
- https://github.com/Luomusha/node-twain
- https://security.snyk.io/vuln/SNYK-JS-NODETWAIN-6421153
