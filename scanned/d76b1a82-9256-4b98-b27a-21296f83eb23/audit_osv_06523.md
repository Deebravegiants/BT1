# [H] BIT-mariadb-2022-32088

## Summary
Severity: High
Advisory: BIT-mariadb-2022-32088
Aliases: BIT-mariadb-min-2022-32088, BIT-mysql-client-2022-32088, CVE-2022-32088
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2022-32088
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.7.0 <10.7.4

## Details
MariaDB v10.2 to v10.7 was discovered to contain a segmentation fault via the component Exec_time_tracker::get_loops/Filesort_tracker::report_use/filesort.

## References
- https://jira.mariadb.org/browse/MDEV-26419
- https://lists.debian.org/debian-lts-announce/2022/09/msg00023.html
- https://security.netapp.com/advisory/ntap-20220818-0005/
- https://nvd.nist.gov/vuln/detail/CVE-2022-32088
