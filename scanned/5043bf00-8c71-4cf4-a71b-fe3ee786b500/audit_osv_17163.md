# [H] CVE-2020-13249

## Summary
Severity: High
Advisory: CVE-2020-13249
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-05-20
Source: https://osv.dev/vulnerability/CVE-2020-13249
Type: osv

## Details
libmariadb/mariadb_lib.c in MariaDB Connector/C before 3.1.8 does not properly validate the content of an OK packet received from a server. NOTE: although mariadb_lib.c was originally based on code shipped for MySQL, this issue does not affect any MySQL components supported by Oracle.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UW2ED32VEUHXFN2J3YQE27JIBV4SC2PI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/X4X2BMF3EILMTXGOZDTPYS3KT5VWLA2P/
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00064.html
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00054.html
- https://github.com/mariadb-corporation/mariadb-connector-c/compare/v3.1.7...v3.1.8
- https://github.com/mariadb-corporation/mariadb-connector-c/commit/2759b87d72926b7c9b5426437a7c8dd15ff57945
