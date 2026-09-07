# [M] easywebpack-cli Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-252h-2cmq-pmr6
CVE: CVE-2020-24855
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-12-15
Source: https://github.com/advisories/GHSA-252h-2cmq-pmr6
Type: github-advisory

## Affected
- npm: `@easy-team/easywebpack-cli` — affected >=0 <4.5.2

## Details
Directory Traversal vulnerability in easywebpack-cli before 4.5.2 allows attackers to obtain sensitive information via crafted GET request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-24855
- https://github.com/easy-team/easywebpack-cli/issues/25
- https://github.com/easy-team/easywebpack-cli/commit/eb3f54603f58ea706d0c03fd6eb76c94176eae52
- https://github.com/easy-team/easywebpack-cli
