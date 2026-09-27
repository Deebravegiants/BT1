# [C] netfilter: require Ethernet MAC header before using eth_hdr()

## Summary
Severity: Critical
Advisory: CVE-2026-53131
Ecosystem: Linux
CVSS: 9.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53131
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: require Ethernet MAC header before using eth_hdr()

`ip6t_eui64`, `xt_mac`, the `bitmap:ip,mac`, `hash:ip,mac`, and
`hash:mac` ipset types, and `nf_log_syslog` access `eth_hdr(skb)`
after either assuming that the skb is associated with an Ethernet
device or checking only that the `ETH_HLEN` bytes at
`skb_mac_header(skb)` lie between `skb->head` and `skb->data`.

Make these paths first verify that the skb is associated with an
Ethernet device, that the MAC header was set, and that it spans at
least a full Ethernet header before accessing `eth_hdr(skb)`.

## References
- https://git.kernel.org/stable/c/063f43361e884acd7300790e90194430275d0d0c
- https://git.kernel.org/stable/c/367abcacc13a8e2e7624408b7f593bd1e60e49d9
- https://git.kernel.org/stable/c/4435888e1bf139d2bfe5911643d4217382136743
- https://git.kernel.org/stable/c/5d634afb8b83b49de562792fd0d047416a43bd4d
- https://git.kernel.org/stable/c/62443dc21114c0bbc476fa62973db89743f2f137
- https://git.kernel.org/stable/c/726abf97566867f808fec9d8a408eb9698bd570a
- https://git.kernel.org/stable/c/cea435ea7e868ea6fdf039bc4f2090c1d829b556
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53131.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53131
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
