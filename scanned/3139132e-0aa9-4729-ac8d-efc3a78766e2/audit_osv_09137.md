# [M] CVE-2016-8578

## Summary
Severity: Medium
Advisory: CVE-2016-8578
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-11-04
Source: https://osv.dev/vulnerability/CVE-2016-8578
Type: osv

## Details
The v9fs_iov_vunmarshal function in fsdev/9p-iov-marshal.c in QEMU (aka Quick Emulator) allows local guest OS administrators to cause a denial of service (NULL pointer dereference and QEMU process crash) by sending an empty string parameter to a 9P operation.

## References
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00140.html
- http://www.openwall.com/lists/oss-security/2016/10/10/14
- http://www.openwall.com/lists/oss-security/2016/10/10/8
- http://www.securityfocus.com/bid/93474
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://security.gentoo.org/glsa/201611-11
- https://lists.gnu.org/archive/html/qemu-devel/2016-09/msg07143.html
