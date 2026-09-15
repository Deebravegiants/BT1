# [M] BIT-mariadb-2024-27766

## Summary
Severity: Medium
Advisory: BIT-mariadb-2024-27766
Aliases: BIT-mariadb-min-2024-27766, BIT-mysql-client-2024-27766, CVE-2024-27766
Ecosystem: Bitnami
Published: 2025-07-11
Source: https://osv.dev/vulnerability/BIT-mariadb-2024-27766
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=11.1.0 <11.1.5

## Details
An issue in MariaDB v.11.1 allows a remote attacker to execute arbitrary code via the lib_mysqludf_sys.so function. NOTE: this is disputed by the MariaDB Foundation because no privilege boundary is crossed.

## References
- https://github.com/Ant1sec-ops/CVE-2024-27766
- https://nvd.nist.gov/vuln/detail/CVE-2024-27766
- https://seclists.org/fulldisclosure/2012/Dec/39
