# [M] BIT-mysql-shell-2026-46869

## Summary
Severity: Medium
Advisory: BIT-mysql-shell-2026-46869
Aliases: CVE-2026-46869
Ecosystem: Bitnami
Published: 2026-06-22
Source: https://osv.dev/vulnerability/BIT-mysql-shell-2026-46869
Type: osv

## Affected
- Bitnami: `mysql-shell` — affected >=9.0.0 <9.7.1

## Details
Vulnerability in the MySQL Shell product of Oracle MySQL (component: Shell: Dump and Load).  Supported versions that are affected are 8.4.0-8.4.9 and  9.0.0-9.7.0. Easily exploitable vulnerability allows unauthenticated attacker with network access via multiple protocols to compromise MySQL Shell.  Successful attacks require human interaction from a person other than the attacker. Successful attacks of this vulnerability can result in  unauthorized access to critical data or complete access to all MySQL Shell accessible data. CVSS 3.1 Base Score 6.5 (Confidentiality impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-46869
- https://www.oracle.com/security-alerts/cspujun2026.html
