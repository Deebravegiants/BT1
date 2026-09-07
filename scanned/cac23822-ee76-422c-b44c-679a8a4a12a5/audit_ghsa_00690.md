# [C] Arbitrary shell command execution in logkitty

## Summary
Severity: Critical
Advisory: GHSA-v8v8-6859-qxm4
CVE: CVE-2020-8149
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-06-05
Source: https://github.com/advisories/GHSA-v8v8-6859-qxm4
Type: github-advisory

## Affected
- npm: `logkitty` — affected >=0 <0.7.1

## Details
Lack of output sanitization allowed an attack to execute arbitrary shell commands via the logkitty npm package before version 0.7.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8149
- https://github.com/zamotany/logkitty/pull/18
- https://github.com/zamotany/logkitty/commit/ef2f673e25c629544dd3de6429999318447dd6bf
- https://hackerone.com/reports/825729
