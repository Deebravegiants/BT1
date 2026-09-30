# [C] xdp: reject clones that overrun skb_shared_info tailroom

## Summary
Severity: Critical
Advisory: CVE-2026-74616
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74616
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

xdp: reject clones that overrun skb_shared_info tailroom

xdpf_clone() clones broadcast copies into a single page and sets
frame_sz to PAGE_SIZE. __xdp_build_skb_from_frame() later treats that
page like a normal XDP frame and expects the usual skb_shared_info
tailroom at the end of the buffer.

The current check only rejects frames whose linear xdp_frame header,
headroom, and packet data exceed PAGE_SIZE. A source frame backed by a
larger allocation can still satisfy that check while extending into the
clone's required shared-info area. When such a clone is converted back
into an skb, build_skb_around() places skb_shared_info over live packet
bytes and later writes can corrupt XDP return metadata.

Reject clones unless their linear area fits inside
SKB_WITH_OVERHEAD(PAGE_SIZE), matching the tailroom requirement already
enforced by the XDP-to-skb conversion path.

## References
- https://git.kernel.org/stable/c/58408982fa39f9758124cec169f42854d6f98f35
- https://git.kernel.org/stable/c/685edea27ac68d08fe4dbd3de74b858d2ad8e830
- https://git.kernel.org/stable/c/ba13763d667e008e185fedf592d53846a5b457d1
- https://git.kernel.org/stable/c/e48e8edbef2eb824201495daa5234560f632b23c
- https://git.kernel.org/stable/c/ef4b7c7046d29a67090de15af0da0d1ae8d1b192
- https://git.kernel.org/stable/c/f463b6f4957c9c3fd1c75f8d3e5af4879fa609c0
- https://git.kernel.org/stable/c/fab820f1691a9e26d9031f18aae1e9ce09078f92
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74616.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74616
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
