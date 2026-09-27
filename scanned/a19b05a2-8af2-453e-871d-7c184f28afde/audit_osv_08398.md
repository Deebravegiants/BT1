# [M] CVE-2016-2847

## Summary
Severity: Medium
Advisory: CVE-2016-2847
CVSS: 6.2 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-27
Source: https://osv.dev/vulnerability/CVE-2016-2847
Type: osv

## Details
fs/pipe.c in the Linux kernel before 4.5 does not limit the amount of unread data in pipes, which allows local users to cause a denial of service (memory consumption) by creating many pipes with non-default sizes.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00060.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://www.oracle.com/technetwork/topics/security/ovmbulletinoct2016-3090547.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00038.html
- http://www.securityfocus.com/bid/83870
- http://www.ubuntu.com/usn/USN-2947-2
- http://www.ubuntu.com/usn/USN-2947-3
- http://www.ubuntu.com/usn/USN-2948-2
- http://www.ubuntu.com/usn/USN-2967-2
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00059.html
- http://rhn.redhat.com/errata/RHSA-2017-0217.html
- http://www.debian.org/security/2016/dsa-3503
- http://www.ubuntu.com/usn/USN-2949-1
- http://www.ubuntu.com/usn/USN-2967-1
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00056.html
- http://rhn.redhat.com/errata/RHSA-2016-2574.html
- http://rhn.redhat.com/errata/RHSA-2016-2584.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00052.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00054.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00000.html
