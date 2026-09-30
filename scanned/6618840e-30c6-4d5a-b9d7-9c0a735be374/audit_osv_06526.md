# [M] BIT-mariadb-2022-38791

## Summary
Severity: Medium
Advisory: BIT-mariadb-2022-38791
Aliases: BIT-mariadb-min-2022-38791, BIT-mysql-client-2022-38791, CVE-2022-38791
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2022-38791
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.9.1 <10.9.2

## Details
In MariaDB before 10.9.2, compress_write in extra/mariabackup/ds_compress.cc does not release data_mutex upon a stream write failure, which allows local users to trigger a deadlock.

## References
- https://jira.mariadb.org/browse/MDEV-28719
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WCOEGSVMIEXDZHBOSV6WVF7FAVRBR2JE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WTVAONAZXJFGHAJ4RP2OF3EAMQCOTDSQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZHISY4YVO4S5QJYYIXCIAXBM7INOL4VY/
- https://security.netapp.com/advisory/ntap-20221104-0008/
- https://nvd.nist.gov/vuln/detail/CVE-2022-38791
