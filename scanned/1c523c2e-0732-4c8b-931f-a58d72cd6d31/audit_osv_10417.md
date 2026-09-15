# [H] CVE-2017-15365

## Summary
Severity: High
Advisory: CVE-2017-15365
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-25
Source: https://osv.dev/vulnerability/CVE-2017-15365
Type: osv

## Details
sql/event_data_objects.cc in MariaDB before 10.1.30 and 10.2.x before 10.2.10 and Percona XtraDB Cluster before 5.6.37-26.21-3 and 5.7.x before 5.7.19-29.22-3 allows remote authenticated users with SQL access to bypass intended access restrictions and replicate data definition language (DDL) statements to cluster nodes by leveraging incorrect ordering of DDL replication and ACL checking.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ELCZV46WIYSJ6VMC65GMNN3A3QDRUJGK/
- https://access.redhat.com/errata/RHSA-2019:1258
- https://mariadb.com/kb/en/library/mariadb-10130-release-notes/
- https://mariadb.com/kb/en/library/mariadb-10210-release-notes/
- https://www.debian.org/security/2018/dsa-4341
- https://www.percona.com/blog/2017/10/30/percona-xtradb-cluster-5-6-37-26-21-3-is-now-available/
- https://www.percona.com/doc/percona-xtradb-cluster/LATEST/release-notes/Percona-XtraDB-Cluster-5.7.19-29.22-3.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1524234
- https://github.com/MariaDB/server/commit/0b5a5258abbeaf8a0c3a18c7e753699787fdf46e
