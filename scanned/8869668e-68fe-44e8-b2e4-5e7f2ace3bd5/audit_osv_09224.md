# [M] CVE-2016-9102

## Summary
Severity: Medium
Advisory: CVE-2016-9102
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-12-09
Source: https://osv.dev/vulnerability/CVE-2016-9102
Type: osv

## Details
Memory leak in the v9fs_xattrcreate function in hw/9pfs/9p.c in QEMU (aka Quick Emulator) allows local guest OS administrators to cause a denial of service (memory consumption and QEMU process crash) via a large number of Txattrcreate messages with the same fid number.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=ff55e94d23ae94c8628b0115320157c763eb3e06
- http://www.openwall.com/lists/oss-security/2016/10/27/15
- http://www.openwall.com/lists/oss-security/2016/10/30/6
- http://www.securityfocus.com/bid/93962
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://security.gentoo.org/glsa/201611-11
- https://lists.gnu.org/archive/html/qemu-devel/2016-10/msg01861.html
