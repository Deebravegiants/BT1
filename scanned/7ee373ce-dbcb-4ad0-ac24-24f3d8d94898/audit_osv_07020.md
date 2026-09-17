# [H] BIT-mysql-shell-2026-46870

## Summary
Severity: High
Advisory: BIT-mysql-shell-2026-46870
Aliases: CVE-2026-46870
Ecosystem: Bitnami
Published: 2026-06-22
Source: https://osv.dev/vulnerability/BIT-mysql-shell-2026-46870
Type: osv

## Affected
- Bitnami: `mysql-shell` — affected >=2026.2.0 <2026.5.0

## Details
Vulnerability in the MySQL Shell product of Oracle MySQL (component: Shell for VS Code).   The supported version that is affected is 2026.2.0+9.6.1. Difficult to exploit vulnerability allows low privileged attacker with network access via multiple protocols to compromise MySQL Shell.  While the vulnerability is in MySQL Shell, attacks may significantly impact additional products (scope change).  Successful attacks of this vulnerability can result in takeover of MySQL Shell. CVSS 3.1 Base Score 8.5 (Confidentiality, Integrity and Availability impacts).  CVSS Vector: (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-46870
- https://www.oracle.com/security-alerts/cspujun2026.html
