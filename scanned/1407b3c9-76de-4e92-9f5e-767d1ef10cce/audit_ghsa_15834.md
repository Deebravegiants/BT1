# [H] MySQL Connector/Python connector takeover vulnerability

## Summary
Severity: High
Advisory: GHSA-hgjp-83m4-h4fj
CVE: CVE-2024-21272
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-10-15
Source: https://github.com/advisories/GHSA-hgjp-83m4-h4fj
Type: github-advisory

## Affected
- PyPI: `mysql-connector-python` — affected >=0 <9.1.0

## Details
Vulnerability in the MySQL Connectors product of Oracle MySQL (component: Connector/Python).  Supported versions that are affected are 9.0.0 and prior. Difficult to exploit vulnerability allows low privileged attacker with network access via multiple protocols to compromise MySQL Connectors.  Successful attacks of this vulnerability can result in takeover of MySQL Connectors. CVSS 3.1 Base Score 7.5 (Confidentiality, Integrity and Availability impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21272
- https://github.com/mysql/mysql-connector-python/commit/e6b927af06e8a85bd3754f602df96a5592b4558c
- https://github.com/mysql/mysql-connector-python
- https://www.oracle.com/security-alerts/cpuoct2024.html
