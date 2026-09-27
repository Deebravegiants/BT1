# [M] CVE-2017-8086

## Summary
Severity: Medium
Advisory: CVE-2017-8086
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-05-02
Source: https://osv.dev/vulnerability/CVE-2017-8086
Type: osv

## Details
Memory leak in the v9fs_list_xattr function in hw/9pfs/9p-xattr.c in QEMU (aka Quick Emulator) allows local guest OS privileged users to cause a denial of service (memory consumption) via vectors involving the orig_value variable.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=4ffcdef4277a91af15a3c09f7d16af072c29f3f2
- http://www.securityfocus.com/bid/98012
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://security.gentoo.org/glsa/201706-03
- http://www.openwall.com/lists/oss-security/2017/04/25/5
- https://bugzilla.redhat.com/show_bug.cgi?id=1444781
- https://lists.gnu.org/archive/html/qemu-devel/2017-04/msg01636.html
