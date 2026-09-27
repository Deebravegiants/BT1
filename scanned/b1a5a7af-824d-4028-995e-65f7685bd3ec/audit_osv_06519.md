# [M] BIT-mariadb-2022-31624

## Summary
Severity: Medium
Advisory: BIT-mariadb-2022-31624
Aliases: BIT-mariadb-min-2022-31624, BIT-mysql-client-2022-31624, CVE-2022-31624
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2022-31624
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.6.0 <10.6.5

## Details
MariaDB Server before 10.7 is vulnerable to Denial of Service. While executing the plugin/server_audit/server_audit.c method log_statement_ex, the held lock lock_bigbuffer is not released correctly, which allows local users to trigger a denial of service due to the deadlock.

## References
- https://github.com/MariaDB/server/commit/d627d00b13ab2f2c0954ea7b77202470cb102944
- https://jira.mariadb.org/browse/MDEV-26556?filter=-2
- https://security.netapp.com/advisory/ntap-20220707-0006/
- https://nvd.nist.gov/vuln/detail/CVE-2022-31624
