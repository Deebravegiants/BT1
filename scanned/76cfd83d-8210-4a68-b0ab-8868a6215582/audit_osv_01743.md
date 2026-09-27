# [H] ALPINE-CVE-2020-13249

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-13249
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-05-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-13249
Type: osv

## Affected
- Alpine:v3.10: `mariadb-connector-c` — affected >=0 <3.0.10-r1
- Alpine:v3.11: `mariadb-connector-c` — affected >=0 <3.1.6-r1
- Alpine:v3.9: `mariadb-connector-c` — affected >=0 <3.0.8-r1

## Details
libmariadb/mariadb_lib.c in MariaDB Connector/C before 3.1.8 does not properly validate the content of an OK packet received from a server. NOTE: although mariadb_lib.c was originally based on code shipped for MySQL, this issue does not affect any MySQL components supported by Oracle.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-13249
