# [M] CVE-2016-2047

## Summary
Severity: Medium
Advisory: CVE-2016-2047
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2016-01-27
Source: https://osv.dev/vulnerability/CVE-2016-2047
Type: osv

## Details
The ssl_verify_server_cert function in sql-common/client.c in MariaDB before 5.5.47, 10.0.x before 10.0.23, and 10.1.x before 10.1.10; Oracle MySQL 5.5.48 and earlier, 5.6.29 and earlier, and 5.7.11 and earlier; and Percona Server do not properly verify that the server hostname matches a domain name in the subject's Common Name (CN) or subjectAltName field of the X.509 certificate, which allows man-in-the-middle attackers to spoof SSL servers via a "/CN=" string in a field in a certificate, as demonstrated by "/OU=/CN=bar.com/CN=foo.com."

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00035.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00053.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00033.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00034.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00051.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00053.html
- http://rhn.redhat.com/errata/RHSA-2016-0534.html
- http://rhn.redhat.com/errata/RHSA-2016-0705.html
- http://rhn.redhat.com/errata/RHSA-2016-1480.html
- http://rhn.redhat.com/errata/RHSA-2016-1481.html
- http://www.debian.org/security/2016/dsa-3453
- http://www.debian.org/security/2016/dsa-3557
- http://www.openwall.com/lists/oss-security/2016/01/26/3
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
- http://www.securityfocus.com/bid/81810
- http://www.securitytracker.com/id/1035606
- http://www.ubuntu.com/usn/USN-2953-1
- http://www.ubuntu.com/usn/USN-2954-1
- https://access.redhat.com/errata/RHSA-2016:1132
- https://mariadb.atlassian.net/browse/MDEV-9212
