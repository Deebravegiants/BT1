# [M] CVE-2017-8379

## Summary
Severity: Medium
Advisory: CVE-2017-8379
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-05-23
Source: https://osv.dev/vulnerability/CVE-2017-8379
Type: osv

## Details
Memory leak in the keyboard input event handlers support in QEMU (aka Quick Emulator) allows local guest OS privileged users to cause a denial of service (host memory consumption) by rapidly generating large keyboard events.

## References
- http://www.securityfocus.com/bid/98277
- https://access.redhat.com/errata/RHSA-2017:2408
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://security.gentoo.org/glsa/201706-03
- http://www.openwall.com/lists/oss-security/2017/05/03/2
- https://lists.gnu.org/archive/html/qemu-devel/2017-04/msg05599.html
