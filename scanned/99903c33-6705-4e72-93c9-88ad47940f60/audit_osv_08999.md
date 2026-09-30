# [M] CVE-2016-7170

## Summary
Severity: Medium
Advisory: CVE-2016-7170
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-10
Source: https://osv.dev/vulnerability/CVE-2016-7170
Type: osv

## Details
The vmsvga_fifo_run function in hw/display/vmware_vga.c in QEMU (aka Quick Emulator) allows local guest OS administrators to cause a denial of service (out-of-bounds write and QEMU process crash) via vectors related to cursor.mask[] and cursor.image[] array sizes when processing a DEFINE_CURSOR svga command.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=167d97a3def77ee2dbf6e908b0ecbfe2103977db
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00140.html
- http://www.openwall.com/lists/oss-security/2016/09/09/4
- http://www.openwall.com/lists/oss-security/2016/09/09/7
- http://www.securityfocus.com/bid/92904
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://lists.gnu.org/archive/html/qemu-devel/2016-09/msg01764.html
