# [M] BIT-mysql-shell-2026-34318

## Summary
Severity: Medium
Advisory: BIT-mysql-shell-2026-34318
Aliases: CVE-2026-34318
Ecosystem: Bitnami
Published: 2026-04-23
Source: https://osv.dev/vulnerability/BIT-mysql-shell-2026-34318
Type: osv

## Affected
- Bitnami: `mysql-shell` — affected >=9.0.0 <9.7.0

## Details
Vulnerability in the MySQL Shell product of Oracle MySQL (component: Shell: Core Client).  Supported versions that are affected are 8.0.0-8.0.45, 8.4.0-8.4.8 and  9.0.0-9.6.0. Difficult to exploit vulnerability allows high privileged attacker with network access via multiple protocols to compromise MySQL Shell.  While the vulnerability is in MySQL Shell, attacks may significantly impact additional products (scope change).  Successful attacks of this vulnerability can result in  unauthorized access to critical data or complete access to all MySQL Shell accessible data. CVSS 3.1 Base Score 5.8 (Confidentiality impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:N/A:N).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-34318
- https://www.oracle.com/security-alerts/cpuapr2026.html
