# [M] CVE-2016-6833

## Summary
Severity: Medium
Advisory: CVE-2016-6833
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-10
Source: https://osv.dev/vulnerability/CVE-2016-6833
Type: osv

## Details
Use-after-free vulnerability in the vmxnet3_io_bar0_write function in hw/net/vmxnet3.c in QEMU (aka Quick Emulator) allows local guest OS administrators to cause a denial of service (QEMU instance crash) by leveraging failure to check if the device is active.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=6c352ca9b4ee3e1e286ea9e8434bd8e69ac7d0d8
- http://www.openwall.com/lists/oss-security/2016/08/12/1
- http://www.openwall.com/lists/oss-security/2016/08/18/3
- http://www.securityfocus.com/bid/93255
- https://lists.debian.org/debian-lts-announce/2018/09/msg00007.html
- https://security.gentoo.org/glsa/201609-01
- https://lists.gnu.org/archive/html/qemu-devel/2016-08/msg01602.html
