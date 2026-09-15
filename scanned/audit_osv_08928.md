# [M] CVE-2016-6836

## Summary
Severity: Medium
Advisory: CVE-2016-6836
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N)
Published: 2016-12-10
Source: https://osv.dev/vulnerability/CVE-2016-6836
Type: osv

## Details
The vmxnet3_complete_packet function in hw/net/vmxnet3.c in QEMU (aka Quick Emulator) allows local guest OS administrators to obtain sensitive host memory information by leveraging failure to initialize the txcq_descr object.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=fdda170e50b8af062cf5741e12c4fb5e57a2eacf
- http://www.openwall.com/lists/oss-security/2016/08/11/5
- http://www.openwall.com/lists/oss-security/2016/08/18/5
- http://www.securityfocus.com/bid/92444
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://security.gentoo.org/glsa/201609-01
- https://lists.gnu.org/archive/html/qemu-devel/2016-08/msg02108.html
