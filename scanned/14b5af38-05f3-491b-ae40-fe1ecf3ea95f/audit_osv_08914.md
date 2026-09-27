# [H] CVE-2016-6664

## Summary
Severity: High
Advisory: CVE-2016-6664
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/CVE-2016-6664
Type: osv

## Details
mysqld_safe in Oracle MySQL through 5.5.51, 5.6.x through 5.6.32, and 5.7.x through 5.7.14; MariaDB; Percona Server before 5.5.51-38.2, 5.6.x before 5.6.32-78-1, and 5.7.x before 5.7.14-8; and Percona XtraDB Cluster before 5.5.41-37.0, 5.6.x before 5.6.32-25.17, and 5.7.x before 5.7.14-26.17, when using file-based logging, allows local users with access to the mysql account to gain root privileges via a symlink attack on error logs and possibly other files.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2130.html
- http://rhn.redhat.com/errata/RHSA-2016-2749.html
- http://seclists.org/fulldisclosure/2016/Nov/4
- http://www.debian.org/security/2017/dsa-3770
- http://www.securityfocus.com/archive/1/539695/100/0/threaded
- http://www.securityfocus.com/bid/93612
- https://access.redhat.com/errata/RHSA-2017:2192
- https://access.redhat.com/errata/RHSA-2018:0279
- https://access.redhat.com/errata/RHSA-2018:0574
- https://security.gentoo.org/glsa/201702-18
- https://www.percona.com/blog/2016/11/02/percona-responds-to-cve-2016-6663-and-cve-2016-6664/
- http://www.oracle.com/technetwork/security-advisory/cpuoct2016-2881722.html
- http://legalhackers.com/advisories/MySQL-Maria-Percona-RootPrivEsc-CVE-2016-6664-5617-Exploit.html
- http://packetstormsecurity.com/files/139491/MySQL-MariaDB-PerconaDB-Root-Privilege-Escalation.html
- https://www.exploit-db.com/exploits/40679/
