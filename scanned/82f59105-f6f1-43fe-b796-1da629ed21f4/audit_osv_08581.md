# [M] CVE-2016-4482

## Summary
Severity: Medium
Advisory: CVE-2016-4482
CVSS: 6.2 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-05-23
Source: https://osv.dev/vulnerability/CVE-2016-4482
Type: osv

## Details
The proc_connectinfo function in drivers/usb/core/devio.c in the Linux kernel through 4.6 does not initialize a certain data structure, which allows local users to obtain sensitive information from kernel stack memory via a crafted USBDEVFS_CONNECTINFO ioctl call.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00044.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00007.html
- http://www.securityfocus.com/bid/90029
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00044.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00055.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/184414.html
- http://www.openwall.com/lists/oss-security/2016/05/04/2
- http://www.ubuntu.com/usn/USN-3021-1
- http://www.ubuntu.com/usn/USN-3021-2
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00054.html
- http://www.ubuntu.com/usn/USN-3016-3
- http://www.ubuntu.com/usn/USN-3017-3
- http://www.ubuntu.com/usn/USN-3018-2
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=681fef8380eb818c0b845fca5d2ab1dcbab114ee
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00056.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00000.html
- http://www.ubuntu.com/usn/USN-3018-1
- http://www.debian.org/security/2016/dsa-3607
- http://www.ubuntu.com/usn/USN-3016-2
- http://www.ubuntu.com/usn/USN-3016-4
