# [M] BIT-mysql-shell-2022-21555

## Summary
Severity: Medium
Advisory: BIT-mysql-shell-2022-21555
Aliases: CVE-2022-21555
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mysql-shell-2022-21555
Type: osv

## Affected
- Bitnami: `mysql-shell` — affected >=0 <1.1.9

## Details
Vulnerability in the MySQL Shell for VS Code product of Oracle MySQL (component: Shell: GUI). Supported versions that are affected are 1.1.8 and prior. Easily exploitable vulnerability allows high privileged attacker with logon to the infrastructure where MySQL Shell for VS Code executes to compromise MySQL Shell for VS Code. Successful attacks require human interaction from a person other than the attacker and while the vulnerability is in MySQL Shell for VS Code, attacks may significantly impact additional products (scope change). Successful attacks of this vulnerability can result in unauthorized update, insert or delete access to some of MySQL Shell for VS Code accessible data as well as unauthorized read access to a subset of MySQL Shell for VS Code accessible data. CVSS 3.1 Base Score 4.2 (Confidentiality and Integrity impacts). CVSS Vector: (CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N).

## References
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://nvd.nist.gov/vuln/detail/CVE-2022-21555
