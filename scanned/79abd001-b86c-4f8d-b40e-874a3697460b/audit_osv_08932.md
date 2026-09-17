# [M] CVE-2016-6888

## Summary
Severity: Medium
Advisory: CVE-2016-6888
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-10
Source: https://osv.dev/vulnerability/CVE-2016-6888
Type: osv

## Details
Integer overflow in the net_tx_pkt_init function in hw/net/net_tx_pkt.c in QEMU (aka Quick Emulator) allows local guest OS administrators to cause a denial of service (QEMU process crash) via the maximum fragmentation count, which triggers an unchecked multiplication and NULL pointer dereference.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=47882fa4975bf0b58dd74474329fdd7154e8f04c
- http://www.openwall.com/lists/oss-security/2016/08/19/10
- http://www.openwall.com/lists/oss-security/2016/08/19/6
- http://www.securityfocus.com/bid/92556
- https://access.redhat.com/errata/RHSA-2017:2392
- https://access.redhat.com/errata/RHSA-2017:2408
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://security.gentoo.org/glsa/201609-01
- https://lists.gnu.org/archive/html/qemu-devel/2016-08/msg03176.html
