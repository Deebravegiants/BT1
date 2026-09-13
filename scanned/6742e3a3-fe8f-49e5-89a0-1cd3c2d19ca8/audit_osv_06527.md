# [M] BIT-mariadb-2022-47015

## Summary
Severity: Medium
Advisory: BIT-mariadb-2022-47015
Aliases: BIT-mariadb-min-2022-47015, BIT-mysql-client-2022-47015, CVE-2022-47015
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-mariadb-2022-47015
Type: osv

## Affected
- Bitnami: `mariadb` — affected >=10.11.0 <10.11.3

## Details
MariaDB Server before 10.3.34 thru 10.9.3 is vulnerable to Denial of Service. It is possible for function spider_db_mbase::print_warnings to dereference a null pointer.

## References
- https://github.com/MariaDB/server/commit/be0a46b3d52b58956fd0d47d040b9f4514406954
- https://lists.debian.org/debian-lts-announce/2023/06/msg00005.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/O22PO3Q6TRSNJI2A2WTJH3VVCHEKBF6C/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SUQ33SPQCZQD63TWAM3XKFNVNFRGPFYU/
- https://security.netapp.com/advisory/ntap-20230309-0009/
- https://nvd.nist.gov/vuln/detail/CVE-2022-47015
