# [C] macvlan: inherit needed_headroom and needed_tailroom from lowerdev

## Summary
Severity: Critical
Advisory: CVE-2026-74743
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-74743
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.23 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

macvlan: inherit needed_headroom and needed_tailroom from lowerdev

macvlan devices inherit hard_header_len from lowerdev during macvlan_init(),
but leave needed_headroom and needed_tailroom set to 0.

When the underlying lowerdev requires extra headroom or tailroom for
headers/trailers (e.g. macsec, ipsec, wireguard, tunnels, or veth with rx
headroom), upper layers calculating packet headroom and tailroom fail to
reserve sufficient space.

This can result in reallocation overhead, skb headroom underflows, or KASAN
slab-use-after-free crashes when dev_hard_header() / macvlan_hard_header()
prepends header data or when lower devices append tailroom.

Fix this by:
1. Inheriting needed_headroom and needed_tailroom from lowerdev in macvlan_init().
2. Propagating needed_headroom and needed_tailroom updates to attached macvlans
   in macvlan_device_event() when receiving NETDEV_FEAT_CHANGE events.

## References
- https://git.kernel.org/stable/c/28afc87bd8da0b3348bbbd834c8a89e83712cf5e
- https://git.kernel.org/stable/c/8cd90e850e434577bf6774778657d26d6995e53f
- https://git.kernel.org/stable/c/8f6a05dbac05725e0786701eb04778c5bdbe4eaa
- https://git.kernel.org/stable/c/96fa90b74385b7f2b0d97251dd43d5ee6ca44668
- https://git.kernel.org/stable/c/bc9a00fb78e32bccc39d763bfd13a450705bac5d
- https://git.kernel.org/stable/c/cef51860becd9700217c81732ca1eb1ea6ed6fe1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74743.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74743
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
