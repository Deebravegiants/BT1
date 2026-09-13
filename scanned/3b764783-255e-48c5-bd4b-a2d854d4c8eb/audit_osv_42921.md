# [H] net: thunderbolt: Fix frags[] overflow by bounding frame_count

## Summary
Severity: High
Advisory: CVE-2026-72157
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72157
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: thunderbolt: Fix frags[] overflow by bounding frame_count

tbnet_poll() assembles a multi-frame ThunderboltIP packet into one skb. The
first frame goes into the skb linear area and every further frame is added as
a page fragment.

	skb_add_rx_frag(skb, skb_shinfo(skb)->nr_frags,
			page, hdr_size, frame_size,
			TBNET_RX_PAGE_SIZE - hdr_size);

A packet of frame_count frames therefore ends up with frame_count - 1
fragments. tbnet_check_frame() only bounds the peer supplied frame_count to
TBNET_RING_SIZE / 4 (64), which is far above MAX_SKB_FRAGS (17 by default). A
peer that sends a packet of 19 or more small frames pushes nr_frags past
MAX_SKB_FRAGS, so skb_add_rx_frag() writes past skb_shinfo()->frags[] and
corrupts memory after the shared info.

Tighten the start of packet bound to MAX_SKB_FRAGS + 1 so a packet can never
produce more fragments than frags[] can hold. This matches the recent skb
frags overflow fixes in other receive paths, for example f0813bcd2d9d ("net:
wwan: t7xx: fix potential skb->frags overflow in RX path") and 600dc40554dc
("net: usb: cdc-phonet: fix skb frags[] overflow in rx_complete()").

## References
- https://git.kernel.org/stable/c/2b3b4e5ff5a58ad32817824b0310e63908b12052
- https://git.kernel.org/stable/c/55d9895f89970501fe126d1026b586b04a224c27
- https://git.kernel.org/stable/c/569ba39b2d12995a29dc158e5b4de6e449278f30
- https://git.kernel.org/stable/c/6262f51e09d8dc8b07599a9e4f03bd3989d13fff
- https://git.kernel.org/stable/c/e27beb4536cbf1d59e2d8c2840e87d972aba906f
- https://git.kernel.org/stable/c/e5824d5b841d99a2bcdd4e2c256643293bbc22c1
- https://git.kernel.org/stable/c/f96b3b35c622d565eff2438993e028d280163f5c
- https://git.kernel.org/stable/c/fe6b606fbf0c3beb94ccf17fcf31d8c2138264e3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72157.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72157
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
