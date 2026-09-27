# [H] netfilter: bridge: make ebt_snat ARP rewrite writable

## Summary
Severity: High
Advisory: CVE-2026-53266
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53266
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: bridge: make ebt_snat ARP rewrite writable

The ebtables SNAT target keeps the Ethernet source address rewrite
behind skb_ensure_writable(skb, 0).  This is intentional: at the bridge
ebtables hooks the Ethernet header is addressed through
skb_mac_header()/eth_hdr(), while skb->data points at the Ethernet
payload.  Asking skb_ensure_writable() for ETH_HLEN bytes would check
the payload, not the Ethernet header, and would reintroduce the small
packet regression fixed by commit 63137bc5882a.

However, the optional ARP sender hardware address rewrite is different.
It writes through skb_store_bits() at an offset relative to skb->data:

        skb_store_bits(skb, sizeof(struct arphdr), info->mac, ETH_ALEN)

skb_header_pointer() only safely reads the ARP header; it does not make
the later sender hardware address range writable.  If that range is
still held in a nonlinear skb fragment backed by a splice-imported file
page, skb_store_bits() maps the frag page and copies the new MAC address
directly into it.

Ensure the ARP SHA range is writable before reading the ARP header and
before calling skb_store_bits().

## References
- https://git.kernel.org/stable/c/153ea96c806aea395daba907a4f88480b6ad5093
- https://git.kernel.org/stable/c/67ba971ae02514d85818fe0c32549ab4bfa3bf49
- https://git.kernel.org/stable/c/76280b78cc9f23bdc6438e10ad6dff148ef8375b
- https://git.kernel.org/stable/c/afd64b59c3de9bbbdd3759e834fdc55cda716e0b
- https://git.kernel.org/stable/c/b18675263db1147c8e1cab625400c13a0d87bd2d
- https://git.kernel.org/stable/c/b7e91939ba9be805a62a257fa4e227dffbb88fa0
- https://git.kernel.org/stable/c/bf84ad7c7a9ede46e31afaa41a1ba06a159e8c87
- https://git.kernel.org/stable/c/c9b5ff59feffb92a147a84a5aa28acd2cb8ff4c5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53266.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53266
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
