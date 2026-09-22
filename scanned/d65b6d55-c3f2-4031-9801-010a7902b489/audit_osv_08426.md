# [M] CVE-2016-3138

## Summary
Severity: Medium
Advisory: CVE-2016-3138
CVSS: 4.6 (CVSS:3.0/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-02
Source: https://osv.dev/vulnerability/CVE-2016-3138
Type: osv

## Details
The acm_probe function in drivers/usb/class/cdc-acm.c in the Linux kernel before 4.5.1 allows physically proximate attackers to cause a denial of service (NULL pointer dereference and system crash) via a USB device without both a control and a data endpoint descriptor.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00054.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00056.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00059.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00060.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00052.html
- http://www.openwall.com/lists/oss-security/2016/03/14/4
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=8835ba4a39cf53f705417b3b3a94eb067673f2c9
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00038.html
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.5.1
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00005.html
- http://www.ubuntu.com/usn/USN-2971-1
- http://www.ubuntu.com/usn/USN-2971-2
- http://www.ubuntu.com/usn/USN-2996-1
- http://www.ubuntu.com/usn/USN-2997-1
- http://www.debian.org/security/2016/dsa-3607
- http://www.ubuntu.com/usn/USN-2968-2
- http://www.ubuntu.com/usn/USN-2970-1
- http://www.ubuntu.com/usn/USN-2969-1
- http://www.ubuntu.com/usn/USN-2968-1
- http://www.ubuntu.com/usn/USN-2971-3
