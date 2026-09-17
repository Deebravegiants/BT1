# [M] CVE-2017-10806

## Summary
Severity: Medium
Advisory: CVE-2017-10806
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-08-02
Source: https://osv.dev/vulnerability/CVE-2017-10806
Type: osv

## Details
Stack-based buffer overflow in hw/usb/redirect.c in QEMU (aka Quick Emulator) allows local guest OS users to cause a denial of service (QEMU process crash) via vectors related to logging debug messages.

## References
- http://www.debian.org/security/2017/dsa-3925
- http://www.securityfocus.com/bid/99475
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- http://www.openwall.com/lists/oss-security/2017/07/07/1
- https://bugzilla.redhat.com/show_bug.cgi?id=1468496
- https://lists.nongnu.org/archive/html/qemu-devel/2017-05/msg03087.html
