# [H] CVE-2016-5244

## Summary
Severity: High
Advisory: CVE-2016-5244
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-06-27
Source: https://osv.dev/vulnerability/CVE-2016-5244
Type: osv

## Details
The rds_inc_info_copy function in net/rds/recv.c in the Linux kernel through 4.6.3 does not initialize a certain structure member, which allows remote attackers to obtain sensitive information from kernel stack memory by reading an RDS message.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00044.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00055.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00044.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00007.html
- http://www.securityfocus.com/bid/91021
- http://www.securitytracker.com/id/1041895
- http://www.ubuntu.com/usn/USN-3072-2
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00000.html
- http://www.ubuntu.com/usn/USN-3070-1
- http://www.ubuntu.com/usn/USN-3071-1
- http://www.ubuntu.com/usn/USN-3071-2
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00054.html
- http://www.debian.org/security/2016/dsa-3607
- http://www.ubuntu.com/usn/USN-3070-4
- http://www.ubuntu.com/usn/USN-3072-1
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00052.html
- http://www.oracle.com/technetwork/security-advisory/cpuoct2018-4428296.html
- http://www.ubuntu.com/usn/USN-3070-2
- http://www.ubuntu.com/usn/USN-3070-3
- https://bugzilla.redhat.com/show_bug.cgi?id=1343337
