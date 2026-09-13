# [H] macsec: don't read an unset MAC header in macsec_encrypt()

## Summary
Severity: High
Advisory: CVE-2026-72019
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72019
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

macsec: don't read an unset MAC header in macsec_encrypt()

macsec_encrypt() reads the Ethernet header via eth_hdr(skb)
(skb->head + skb->mac_header) to memmove() the 12 source/destination MAC
bytes forward and make room for the SecTAG.

On the AF_PACKET SOCK_RAW + PACKET_QDISC_BYPASS transmit path the skb
reaches the macsec ndo_start_xmit() with the MAC header unset, so
eth_hdr(skb) resolves to skb->head + (u16)~0 and the read is out of
bounds: a 12-byte heap over-read that is also emitted on the wire as the
frame's outer source/destination MAC. KASAN reports a slab-out-of-bounds
read in macsec_start_xmit() on 6.0; on current mainline a CONFIG_DEBUG_NET
build flags it as an unset mac header in skb_mac_header().

On the TX path the L2 header is at skb->data, so use skb_eth_hdr(), added
by commit 96cc4b69581d ("macvlan: do not assume mac_header is set in
macvlan_broadcast()") for exactly this purpose.

## References
- https://git.kernel.org/stable/c/2cf10d042562283ff4ae97c02d0993d4f1b5ea29
- https://git.kernel.org/stable/c/3adea1b1c04b57e08a5c12a1f42483760581ce61
- https://git.kernel.org/stable/c/b6cec6187b8632423cd99a94fd5e5ba165fa2a33
- https://git.kernel.org/stable/c/c39087ad0b97fc11a3b058dfc8db9fd370762cb9
- https://git.kernel.org/stable/c/dc9ffa1905e72f026d080880a2e4cfc42aa91000
- https://git.kernel.org/stable/c/e17a42199824973cd8212e95b21ffadf4114a21b
- https://git.kernel.org/stable/c/f21fa533a3ed15ada74106aac4b9ddd078fc6b7a
- https://git.kernel.org/stable/c/f5089008f90c0a7c5520dff3934e0af00adf322d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72019.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72019
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
