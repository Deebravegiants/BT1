# [M] BIT-mysql-shell-2026-34319

## Summary
Severity: Medium
Advisory: BIT-mysql-shell-2026-34319
Aliases: CVE-2026-34319
Ecosystem: Bitnami
Published: 2026-04-23
Source: https://osv.dev/vulnerability/BIT-mysql-shell-2026-34319
Type: osv

## Affected
- Bitnami: `mysql-shell` — affected >=9.0.0 <9.7.0

## Details
Vulnerability in the MySQL Shell product of Oracle MySQL (component: Shell: Core Client).  Supported versions that are affected are 8.0.0-8.0.45, 8.4.0-8.4.8 and  9.0.0-9.6.0. Easily exploitable vulnerability allows low privileged attacker with logon to the infrastructure where MySQL Shell executes to compromise MySQL Shell.  Successful attacks require human interaction from a person other than the attacker. Successful attacks of this vulnerability can result in unauthorized ability to cause a hang or frequently repeatable crash (complete DOS) of MySQL Shell. CVSS 3.1 Base Score 5.0 (Availability impacts).  CVSS Vector: (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-34319
- https://www.oracle.com/security-alerts/cpuapr2026.html
