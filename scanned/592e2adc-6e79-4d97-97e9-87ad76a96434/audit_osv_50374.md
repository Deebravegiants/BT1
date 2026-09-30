# [M] CVE-2020-14331

## Summary
Severity: Medium
Advisory: CVE-2020-14331
CVSS: 6.6 (CVSS:3.1/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-15
Source: https://osv.dev/vulnerability/CVE-2020-14331
Type: osv

## Details
A flaw was found in the Linux kernel’s implementation of the invert video code on VGA consoles when a local attacker attempts to resize the console, calling an ioctl VT_RESIZE, which causes an out-of-bounds write to occur. This flaw allows a local user with access to the VGA console to crash the system, potentially escalating their privileges on the system. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://lists.debian.org/debian-lts-announce/2020/09/msg00025.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00032.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00034.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1858679
- https://lists.openwall.net/linux-kernel/2020/07/29/234
- https://www.openwall.com/lists/oss-security/2020/07/28/2
