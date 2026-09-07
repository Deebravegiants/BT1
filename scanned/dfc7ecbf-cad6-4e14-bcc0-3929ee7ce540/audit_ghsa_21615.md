# [M] Prototype Pollution in keyget

## Summary
Severity: Medium
Advisory: GHSA-9fp7-4fjm-q3mf
CVE: CVE-2021-23760
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-02-01
Source: https://github.com/advisories/GHSA-9fp7-4fjm-q3mf
Type: github-advisory

## Affected
- npm: `keyget` — affected >=0

## Details
The package keyget from 0.0.0 are vulnerable to Prototype Pollution via the methods set, push, and at which could allow an attacker to cause a denial of service and may lead to remote code execution. **Note:** This vulnerability derives from an incomplete fix to [CVE-2020-28272](https://security.snyk.io/vuln/SNYK-JS-KEYGET-1048048)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23760
- https://github.com/rumkin/keyget
- https://security.snyk.io/vuln/SNYK-JS-KEYGET-1048048
- https://snyk.io/vuln/SNYK-JS-KEYGET-2342624
