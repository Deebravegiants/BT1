# [H] CVE-2017-6058

## Summary
Severity: High
Advisory: CVE-2017-6058
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-20
Source: https://osv.dev/vulnerability/CVE-2017-6058
Type: osv

## Details
Buffer overflow in NetRxPkt::ehdr_buf in hw/net/net_rx_pkt.c in QEMU (aka Quick Emulator), when the VLANSTRIP feature is enabled on the vmxnet3 device, allows remote attackers to cause a denial of service (out-of-bounds access and QEMU process crash) via vectors related to VLAN stripping.

## References
- http://git.qemu-project.org/?p=qemu.git%3Ba=commit%3Bh=df8bf7a7fe75eb5d5caffa55f5cd4292b757aea6
- http://www.securityfocus.com/bid/96277
- http://www.securitytracker.com/id/1037856
- https://security.gentoo.org/glsa/201704-01
- http://www.openwall.com/lists/oss-security/2017/02/17/2
- https://bugzilla.redhat.com/show_bug.cgi?id=1423358
- https://lists.nongnu.org/archive/html/qemu-devel/2017-02/msg03527.html
