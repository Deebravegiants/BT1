# [M] OpenCRX vulnerable to password enumeration via error messages in password reset

## Summary
Severity: Medium
Advisory: GHSA-j5v3-363p-g843
CVE: CVE-2022-40084
CWE: CWE-203
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-10-20
Source: https://github.com/advisories/GHSA-j5v3-363p-g843
Type: github-advisory

## Affected
- Maven: `org.opencrx:opencrx-client` — affected >=0 <5.2.2

## Details
OpenCRX before v5.2.2 was discovered to be vulnerable to password enumeration due to the difference in error messages received during a password reset which could enable an attacker to determine if a username, email or ID is valid.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40084
- https://cwe.mitre.org/data/definitions/204.html
- https://github.com/ciph0x01/OpenCRX-CVE/blob/main/CVE-2022-40084.md
