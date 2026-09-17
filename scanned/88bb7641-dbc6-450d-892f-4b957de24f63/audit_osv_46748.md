# [M] CVE-2015-1027

## Summary
Severity: Medium
Advisory: CVE-2015-1027
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-09-29
Source: https://osv.dev/vulnerability/CVE-2015-1027
Type: osv

## Details
The version checking subroutine in percona-toolkit before 2.2.13 and xtrabackup before 2.2.9 was vulnerable to silent HTTP downgrade attacks and Man In The Middle attacks in which the server response could be modified to allow the attacker to respond with modified command payload and have the client return additional running configuration information leading to an information disclosure of running configuration of MySQL.

## References
- https://bugs.launchpad.net/percona-toolkit/+bug/1408375
- https://www.percona.com/blog/2015/05/06/percona-security-advisory-cve-2015-1027/
- https://www.percona.com/blog/2015/05/06/percona-security-advisory-cve-2015-1027/
- https://bugs.launchpad.net/percona-toolkit/+bug/1408375
