# [H] CVE-2016-6663

## Summary
Severity: High
Advisory: CVE-2016-6663
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/CVE-2016-6663
Type: osv

## Details
Race condition in Oracle MySQL before 5.5.52, 5.6.x before 5.6.33, 5.7.x before 5.7.15, and 8.x before 8.0.1; MariaDB before 5.5.52, 10.0.x before 10.0.28, and 10.1.x before 10.1.18; Percona Server before 5.5.51-38.2, 5.6.x before 5.6.32-78-1, and 5.7.x before 5.7.14-8; and Percona XtraDB Cluster before 5.5.41-37.0, 5.6.x before 5.6.32-25.17, and 5.7.x before 5.7.14-26.17 allows local users with certain permissions to gain privileges by leveraging use of my_copystat by REPAIR TABLE to repair a MyISAM table.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2130.html
- http://rhn.redhat.com/errata/RHSA-2016-2131.html
- http://rhn.redhat.com/errata/RHSA-2016-2595.html
- http://rhn.redhat.com/errata/RHSA-2016-2749.html
- http://rhn.redhat.com/errata/RHSA-2016-2927.html
- http://rhn.redhat.com/errata/RHSA-2016-2928.html
- http://rhn.redhat.com/errata/RHSA-2017-0184.html
- http://seclists.org/fulldisclosure/2016/Nov/4
- http://www.openwall.com/lists/oss-security/2016/10/25/4
- http://www.securityfocus.com/bid/92911
- http://www.securityfocus.com/bid/93614
- https://mariadb.com/kb/en/mariadb/mariadb-10028-release-notes/
- https://mariadb.com/kb/en/mariadb/mariadb-10118-release-notes/
- https://mariadb.com/kb/en/mariadb/mariadb-5552-release-notes/
- https://www.percona.com/blog/2016/11/02/percona-responds-to-cve-2016-6663-and-cve-2016-6664/
- https://dev.mysql.com/doc/relnotes/mysql/5.5/en/news-5-5-52.html
- https://dev.mysql.com/doc/relnotes/mysql/5.6/en/news-5-6-33.html
- https://dev.mysql.com/doc/relnotes/mysql/5.7/en/news-5-7-15.html
- https://dev.mysql.com/doc/relnotes/mysql/8.0/en/news-8-0-1.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2016-2881722.html
