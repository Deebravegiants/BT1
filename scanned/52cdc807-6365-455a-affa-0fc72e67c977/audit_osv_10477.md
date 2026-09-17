# [H] CVE-2017-15945

## Summary
Severity: High
Advisory: CVE-2017-15945
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-27
Source: https://osv.dev/vulnerability/CVE-2017-15945
Type: osv

## Details
The installation scripts in the Gentoo dev-db/mysql, dev-db/mariadb, dev-db/percona-server, dev-db/mysql-cluster, and dev-db/mariadb-galera packages before 2017-09-29 have chown calls for user-writable directory trees, which allows local users to gain privileges by leveraging access to the mysql account for creation of a link.

## References
- https://bugs.gentoo.org/630822
- https://security.gentoo.org/glsa/201711-04
