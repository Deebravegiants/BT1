# [M] BIT-mariadb-2023-39593

## Summary
Severity: Medium
Advisory: BIT-mariadb-2023-39593
Aliases: BIT-mariadb-min-2023-39593, BIT-mysql-client-2023-39593, CVE-2023-39593
Ecosystem: Bitnami
Published: 2025-07-11
Source: https://osv.dev/vulnerability/BIT-mariadb-2023-39593
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.5.0

## Details
Insecure permissions in the sys_exec function of MariaDB v10.5 allows authenticated attackers to execute arbitrary commands with elevated privileges. NOTE: this is disputed by the MariaDB Foundation because no privilege boundary is crossed.

## References
- https://github.com/Ant1sec-ops/CVE-2023-39593
- https://nvd.nist.gov/vuln/detail/CVE-2023-39593
- https://seclists.org/fulldisclosure/2012/Dec/39
