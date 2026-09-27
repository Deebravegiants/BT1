# [H] BIT-mariadb-2022-32091

## Summary
Severity: High
Advisory: BIT-mariadb-2022-32091
Aliases: BIT-mariadb-min-2022-32091, BIT-mysql-client-2022-32091, CVE-2022-32091
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2022-32091
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.9.0 <10.9.2

## Details
MariaDB v10.7 was discovered to contain an use-after-poison in in __interceptor_memset at /libsanitizer/sanitizer_common/sanitizer_common_interceptors.inc.

## References
- https://jira.mariadb.org/browse/MDEV-26431
- https://lists.debian.org/debian-lts-announce/2022/09/msg00023.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WCOEGSVMIEXDZHBOSV6WVF7FAVRBR2JE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WTVAONAZXJFGHAJ4RP2OF3EAMQCOTDSQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZHISY4YVO4S5QJYYIXCIAXBM7INOL4VY/
- https://security.netapp.com/advisory/ntap-20220818-0005/
- https://nvd.nist.gov/vuln/detail/CVE-2022-32091
