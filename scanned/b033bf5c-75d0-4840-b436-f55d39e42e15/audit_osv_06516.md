# [M] BIT-mariadb-2022-31621

## Summary
Severity: Medium
Advisory: BIT-mariadb-2022-31621
Aliases: BIT-mariadb-min-2022-31621, BIT-mysql-client-2022-31621, CVE-2022-31621
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2022-31621
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.6.0 <10.6.5

## Details
MariaDB Server before 10.7 is vulnerable to Denial of Service. In extra/mariabackup/ds_xbstream.cc, when an error occurs (stream_ctxt->dest_file == NULL) while executing the method xbstream_open, the held lock is not released correctly, which allows local users to trigger a denial of service due to the deadlock. Note: The vendor argues this is just an improper locking bug and not a vulnerability with adverse effects.

## References
- https://github.com/MariaDB/server/commit/b1351c15946349f9daa7e5297fb2ac6f3139e4a8
- https://jira.mariadb.org/browse/MDEV-26574?filter=-2
- https://security.netapp.com/advisory/ntap-20220707-0006/
- https://jira.mariadb.org/browse/MDEV-26561
- https://jira.mariadb.org/browse/MDEV-26574
- https://nvd.nist.gov/vuln/detail/CVE-2022-31621
