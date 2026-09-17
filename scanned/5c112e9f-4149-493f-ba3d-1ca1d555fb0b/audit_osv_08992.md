# [C] CVE-2016-7161

## Summary
Severity: Critical
Advisory: CVE-2016-7161
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-10-05
Source: https://osv.dev/vulnerability/CVE-2016-7161
Type: osv

## Details
Heap-based buffer overflow in the .receive callback of xlnx.xps-ethernetlite in QEMU (aka Quick Emulator) allows attackers to execute arbitrary code on the QEMU host via a large ethlite packet.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=a0d1cbdacff5df4ded16b753b38fdd9da6092968
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00140.html
- http://www.openwall.com/lists/oss-security/2016/09/23/6
- http://www.openwall.com/lists/oss-security/2016/09/23/8
- http://www.securityfocus.com/bid/93141
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://security.gentoo.org/glsa/201611-11
- https://lists.gnu.org/archive/html/qemu-devel/2016-08/msg01598.html
- https://lists.gnu.org/archive/html/qemu-devel/2016-08/msg01877.html
