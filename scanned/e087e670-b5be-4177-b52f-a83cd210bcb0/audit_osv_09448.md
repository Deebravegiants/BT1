# [M] CVE-2016-9913

## Summary
Severity: Medium
Advisory: CVE-2016-9913
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-12-29
Source: https://osv.dev/vulnerability/CVE-2016-9913
Type: osv

## Details
Memory leak in the v9fs_device_unrealize_common function in hw/9pfs/9p.c in QEMU (aka Quick Emulator) allows local privileged guest OS users to cause a denial of service (host memory consumption and possibly QEMU process crash) via vectors involving the order of resource cleanup.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=4774718e5c194026ba5ee7a28d9be49be3080e42
- http://www.openwall.com/lists/oss-security/2016/12/06/11
- http://www.openwall.com/lists/oss-security/2016/12/08/7
- http://www.securityfocus.com/bid/94729
- https://security.gentoo.org/glsa/201701-49
- https://lists.gnu.org/archive/html/qemu-devel/2016-11/msg03278.html
