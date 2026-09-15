# [C] vxlan: use pskb_network_may_pull() for transmit path header pulls

## Summary
Severity: Critical
Advisory: CVE-2026-74474
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74474
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

vxlan: use pskb_network_may_pull() for transmit path header pulls

In vxlan_xmit(), arp_reduce(), and vxlan_mdb_entry_skb_get(), pskb_may_pull() was
being called to verify the availability of network layer headers (ARP, IPv6/ND,
IP/IPv6 MDB keys).

However, during transmit skb->data points to the MAC header, so skb_network_offset(skb)
is ETH_HLEN (14 bytes). Using pskb_may_pull(skb, len) only checks len bytes from skb->data
rather than skb_network_offset(skb) + len, which can leave part of the network header
in non-linear frags.

Replace these remaining pskb_may_pull() calls with pskb_network_may_pull() to properly
account for the MAC header offset.

## References
- https://git.kernel.org/stable/c/6146901881f09ef063eb34ad389f63231f8486f5
- https://git.kernel.org/stable/c/7076a34b6e33315dc160b4612bfea1c597495585
- https://git.kernel.org/stable/c/94dee751aad627b3645d424b5d0c736d394573e9
- https://git.kernel.org/stable/c/b9553558b48db54ac9273e6b98d7263ef5c1a329
- https://git.kernel.org/stable/c/bb01c51950c3ff3c76acdd54b85ab38ccc2a8bb4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74474.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74474
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
