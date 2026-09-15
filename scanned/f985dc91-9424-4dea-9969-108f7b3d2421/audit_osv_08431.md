# [M] CVE-2016-3156

## Summary
Severity: Medium
Advisory: CVE-2016-3156
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-04-27
Source: https://osv.dev/vulnerability/CVE-2016-3156
Type: osv

## Details
The IPv4 implementation in the Linux kernel before 4.5.2 mishandles destruction of device objects, which allows guest OS users to cause a denial of service (host OS networking outage) by arranging for a large number of IP addresses.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00019.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00038.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00060.html
- http://www.openwall.com/lists/oss-security/2016/03/15/3
- http://www.oracle.com/technetwork/topics/security/ovmbulletinoct2016-3090547.html
- http://www.securityfocus.com/bid/84428
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=fbd40ea0180a2d328c5adc61414dc8bab9335ce2
- http://rhn.redhat.com/errata/RHSA-2016-2584.html
- http://www.debian.org/security/2016/dsa-3607
- http://www.ubuntu.com/usn/USN-2969-1
- http://www.ubuntu.com/usn/USN-2971-1
- http://www.ubuntu.com/usn/USN-2971-2
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00054.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00059.html
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00005.html
- http://www.ubuntu.com/usn/USN-2971-3
- http://www.ubuntu.com/usn/USN-2996-1
- http://www.ubuntu.com/usn/USN-2997-1
- http://www.ubuntu.com/usn/USN-2968-1
