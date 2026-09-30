# [M] CVE-2016-6834

## Summary
Severity: Medium
Advisory: CVE-2016-6834
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-10
Source: https://osv.dev/vulnerability/CVE-2016-6834
Type: osv

## Details
The net_tx_pkt_do_sw_fragmentation function in hw/net/net_tx_pkt.c in QEMU (aka Quick Emulator) allows local guest OS administrators to cause a denial of service (infinite loop and QEMU process crash) via a zero length for the current fragment length.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=ead315e43ea0c2ca3491209c6c8db8ce3f2bbe05
- http://www.openwall.com/lists/oss-security/2016/08/11/8
- http://www.openwall.com/lists/oss-security/2016/08/18/7
- http://www.securityfocus.com/bid/92446
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://security.gentoo.org/glsa/201609-01
- https://lists.gnu.org/archive/html/qemu-devel/2016-08/msg01601.html
