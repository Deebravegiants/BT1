# [M] BIT-mariadb-2026-35549

## Summary
Severity: Medium
Advisory: BIT-mariadb-2026-35549
Aliases: BIT-mariadb-min-2026-35549, BIT-mysql-client-2026-35549, CVE-2026-35549
Ecosystem: Bitnami
Published: 2026-06-05
Source: https://osv.dev/vulnerability/BIT-mariadb-2026-35549
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=12.0.0 <12.2.2

## Details
An issue was discovered in MariaDB Server before 11.4.10, 11.5.x through 11.8.x before 11.8.6, and 12.x before 12.2.2. If the caching_sha2_password authentication plugin is installed, and some user accounts are configured to use it, a large packet can crash the server because sha256_crypt_r uses alloca.

## References
- https://jira.mariadb.org/browse/MDEV-38365
- https://nvd.nist.gov/vuln/detail/CVE-2026-35549
