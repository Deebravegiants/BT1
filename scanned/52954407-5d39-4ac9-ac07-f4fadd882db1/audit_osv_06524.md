# [H] BIT-mariadb-2022-32089

## Summary
Severity: High
Advisory: BIT-mariadb-2022-32089
Aliases: BIT-mariadb-min-2022-32089, BIT-mysql-client-2022-32089, CVE-2022-32089
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2022-32089
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.9.0 <10.9.2

## Details
MariaDB v10.5 to v10.7 was discovered to contain a segmentation fault via the component st_select_lex_unit::exclude_level.

## References
- https://jira.mariadb.org/browse/MDEV-26410
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WCOEGSVMIEXDZHBOSV6WVF7FAVRBR2JE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WTVAONAZXJFGHAJ4RP2OF3EAMQCOTDSQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZHISY4YVO4S5QJYYIXCIAXBM7INOL4VY/
- https://security.netapp.com/advisory/ntap-20220818-0005/
- https://nvd.nist.gov/vuln/detail/CVE-2022-32089
