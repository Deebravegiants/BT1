# [H] CVE-2016-5829

## Summary
Severity: High
Advisory: CVE-2016-5829
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-06-27
Source: https://osv.dev/vulnerability/CVE-2016-5829
Type: osv

## Details
Multiple heap-based buffer overflows in the hiddev_ioctl_usage function in drivers/hid/usbhid/hiddev.c in the Linux kernel through 4.6.3 allow local users to cause a denial of service or possibly have unspecified other impact via a crafted (1) HIDIOCGUSAGES or (2) HIDIOCSUSAGES ioctl call.

## References
- http://www.ubuntu.com/usn/USN-3071-2
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00054.html
- http://rhn.redhat.com/errata/RHSA-2016-2584.html
- http://www.ubuntu.com/usn/USN-3070-4
- http://www.ubuntu.com/usn/USN-3071-1
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00027.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00050.html
- http://rhn.redhat.com/errata/RHSA-2016-2574.html
- http://www.ubuntu.com/usn/USN-3072-1
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00007.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00048.html
- http://www.ubuntu.com/usn/USN-3070-2
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00053.html
- http://www.ubuntu.com/usn/USN-3070-1
- http://www.ubuntu.com/usn/USN-3072-2
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=93a2001bdfd5376c3dc2158653034c20392d15c5
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00049.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00000.html
- http://www.debian.org/security/2016/dsa-3616
- http://www.oracle.com/technetwork/topics/security/linuxbulletinoct2016-3090545.html
