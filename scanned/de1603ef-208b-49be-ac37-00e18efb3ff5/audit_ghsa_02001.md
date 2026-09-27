# [C] Prototype Pollution

## Summary
Severity: Critical
Advisory: GHSA-x3wr-v4wx-5qpc
CVE: CVE-2021-25948
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-21
Source: https://github.com/advisories/GHSA-x3wr-v4wx-5qpc
Type: github-advisory

## Affected
- npm: `expand-hash` — affected >=0

## Details
Prototype pollution vulnerability in ‘expand-hash’ versions 0.1.0 through 1.0.1 allows an attacker to cause a denial of service and may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25948
- https://github.com/doowb/expand-hash
- https://github.com/doowb/expand-hash/blob/556913f6c2f05848110b5b8261cfc78e5ce3dc77/index.js#L19
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25948
