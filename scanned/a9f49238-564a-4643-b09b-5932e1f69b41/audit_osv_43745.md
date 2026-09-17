# [H] net/packet: reset the MAC header on the packet-socket transmit path

## Summary
Severity: High
Advisory: CVE-2026-74667
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74667
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/packet: reset the MAC header on the packet-socket transmit path

packet_parse_headers() resets the MAC header only for a SOCK_RAW frame
whose socket did not bind a protocol. A protocol-bound SOCK_RAW socket,
any SOCK_DGRAM frame, and the legacy SOCK_PACKET path therefore leave
skb->mac_header unset here.

For frames sent via __dev_queue_xmit() this is harmless: it resets the
MAC header unconditionally. But the packet-socket PACKET_QDISC_BYPASS
path uses dev_direct_xmit(), which does not, so the frame reaches
ndo_start_xmit() with the MAC header unset. A driver that reads
eth_hdr(skb) on transmit then dereferences skb->head + (u16)~0, an
out-of-bounds access ~64 KiB past the head -- the same class fixed for
one consumer in commit f5089008f90c ("macsec: do not read an unset MAC
header in macsec_encrypt()").

packet_parse_headers() runs only on the transmit path, where skb->data
points at the start of the L2 header for every packet-socket type
regardless of its length: SOCK_RAW and SOCK_PACKET carry a user-supplied
header and SOCK_DGRAM has one built by dev_hard_header(). Reset the MAC
header unconditionally, mirroring __dev_queue_xmit(), so the frame is
anchored on the bypass path too.

Found by 0sec (https://0sec.ai) using automated source analysis;
verified against source and matched to the macsec KASAN report in
f5089008f90c. Compile-tested.

## References
- https://git.kernel.org/stable/c/1e43a1d66615f411d427f9df1f46dd049d9e3681
- https://git.kernel.org/stable/c/2610ed4e86a4590234a9d70518c469751c5af231
- https://git.kernel.org/stable/c/284f3e7a3f1a743fdf89e304fd1f19d5ffcff46d
- https://git.kernel.org/stable/c/4057853a91fb796c4f47c7d1baf1aa085394148e
- https://git.kernel.org/stable/c/971aa7d99242bbf09513e27b7a243f0b29ff23ae
- https://git.kernel.org/stable/c/b47ba8fe6e1d2df8c92048de5afafd059447dc30
- https://git.kernel.org/stable/c/c2707480cfbf19c7619acc9c089d17f20869821f
- https://git.kernel.org/stable/c/fdd4d7d52358a58e351dd9d82530c04eba8ccd7a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74667.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74667
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
