# [M] BIT-mariadb-2022-31622

## Summary
Severity: Medium
Advisory: BIT-mariadb-2022-31622
Aliases: BIT-mariadb-min-2022-31622, BIT-mysql-client-2022-31622, CVE-2022-31622
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2022-31622
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.7.0 <10.7.2

## Details
MariaDB Server before 10.7 is vulnerable to Denial of Service. In extra/mariabackup/ds_compress.cc, when an error occurs (pthread_create returns a nonzero value) while executing the method create_worker_threads, the held lock is not released correctly, which allows local users to trigger a denial of service due to the deadlock. Note: The vendor argues this is just an improper locking bug and not a vulnerability with adverse effects.

## References
- https://github.com/MariaDB/server/commit/e1eb39a446c30b8459c39fd7f2ee1c55a36e97d2
- https://jira.mariadb.org/browse/MDEV-26561?filter=-2
- https://security.netapp.com/advisory/ntap-20220707-0006/
- https://jira.mariadb.org/browse/MDEV-26561
- https://jira.mariadb.org/browse/MDEV-26574
- https://nvd.nist.gov/vuln/detail/CVE-2022-31622
