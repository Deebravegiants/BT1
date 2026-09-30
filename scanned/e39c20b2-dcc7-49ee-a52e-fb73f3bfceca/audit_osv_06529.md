# [C] BIT-mariadb-2023-26785

## Summary
Severity: Critical
Advisory: BIT-mariadb-2023-26785
Aliases: BIT-mariadb-min-2023-26785, BIT-mysql-client-2023-26785, CVE-2023-26785
Ecosystem: Bitnami
Published: 2025-07-11
Source: https://osv.dev/vulnerability/BIT-mariadb-2023-26785
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.5.0

## Details
MariaDB v10.5 was discovered to contain a remote code execution (RCE) vulnerability via UDF Code in a Shared Object File, followed by a "create function" statement. NOTE: this is disputed by the MariaDB Foundation because no privilege boundary is crossed.

## References
- https://github.com/Ant1sec-ops/CVE-2023-26785
- https://nvd.nist.gov/vuln/detail/CVE-2023-26785
- https://seclists.org/fulldisclosure/2012/Dec/39
