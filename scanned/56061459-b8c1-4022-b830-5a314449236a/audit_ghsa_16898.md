# [M] mysql2 cache poisoning vulnerability

## Summary
Severity: Medium
Advisory: GHSA-mqr2-w7wj-jjgr
CVE: CVE-2024-21507
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2024-04-10
Source: https://github.com/advisories/GHSA-mqr2-w7wj-jjgr
Type: github-advisory

## Affected
- npm: `mysql2` — affected >=0 <3.9.3

## Details
Versions of the package mysql2 before 3.9.3 are vulnerable to Improper Input Validation through the `keyFromFields` function, resulting in cache poisoning. An attacker can inject a colon `:` character within a value of the attacker-crafted key.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21507
- https://github.com/sidorares/node-mysql2/pull/2424
- https://github.com/sidorares/node-mysql2/commit/0d54b0ca6498c823098426038162ef10df02c818
- https://blog.slonser.info/posts/mysql2-attacker-configuration
- https://github.com/sidorares/node-mysql2
- https://security.snyk.io/vuln/SNYK-JS-MYSQL2-6591300
