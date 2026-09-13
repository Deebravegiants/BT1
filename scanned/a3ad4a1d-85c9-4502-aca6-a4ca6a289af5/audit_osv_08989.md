# [M] CVE-2016-7155

## Summary
Severity: Medium
Advisory: CVE-2016-7155
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-10
Source: https://osv.dev/vulnerability/CVE-2016-7155
Type: osv

## Details
hw/scsi/vmw_pvscsi.c in QEMU (aka Quick Emulator) allows local guest OS administrators to cause a denial of service (out-of-bounds access or infinite loop, and QEMU process crash) via a crafted page count for descriptor rings.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=7f61f4690dd153be98900a2a508b88989e692753
- http://www.openwall.com/lists/oss-security/2016/09/06/2
- http://www.openwall.com/lists/oss-security/2016/09/07/1
- http://www.securityfocus.com/bid/92772
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://lists.gnu.org/archive/html/qemu-devel/2016-09/msg00050.html
