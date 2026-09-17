# [M] BIT-mariadb-2022-31623

## Summary
Severity: Medium
Advisory: BIT-mariadb-2022-31623
Aliases: BIT-mariadb-min-2022-31623, BIT-mysql-client-2022-31623, CVE-2022-31623
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2022-31623
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.7.0 <10.7.2

## Details
MariaDB Server before 10.7 is vulnerable to Denial of Service. In extra/mariabackup/ds_compress.cc, when an error occurs (i.e., going to the err label) while executing the method create_worker_threads, the held lock thd->ctrl_mutex is not released correctly, which allows local users to trigger a denial of service due to the deadlock. Note: The vendor argues this is just an improper locking bug and not a vulnerability with adverse effects.

## References
- https://github.com/MariaDB/server/commit/7c30bc38a588b22b01f11130cfe99e7f36accf94
- https://github.com/MariaDB/server/pull/1938
- https://security.netapp.com/advisory/ntap-20220707-0006/
- https://jira.mariadb.org/browse/MDEV-26561
- https://jira.mariadb.org/browse/MDEV-26574
- https://nvd.nist.gov/vuln/detail/CVE-2022-31623
