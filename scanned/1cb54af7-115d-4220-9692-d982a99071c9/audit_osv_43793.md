# [C] ipvlan: inherit needed_headroom and needed_tailroom from phy_dev

## Summary
Severity: Critical
Advisory: CVE-2026-74744
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-74744
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipvlan: inherit needed_headroom and needed_tailroom from phy_dev

ipvlan devices inherit hard_header_len from phy_dev during ipvlan_init(),
but leave needed_headroom and needed_tailroom set to 0.

When the underlying phy_dev (or stacked lower device) requires extra headroom
or tailroom for headers/trailers (e.g. macsec, ipsec, wireguard, tunnels, or
veth with rx headroom), upper layers calculating packet headroom and tailroom
fail to reserve sufficient space.

This can result in reallocation overhead, skb headroom underflows, or KASAN
slab-use-after-free crashes when dev_hard_header() / ipvlan_hard_header()
prepends header data or when lower devices append tailroom.

Fix this by:
1. Inheriting needed_headroom and needed_tailroom from phy_dev in ipvlan_init().
2. Propagating needed_headroom and needed_tailroom updates to attached ipvlans
   in ipvlan_device_event() when receiving NETDEV_FEAT_CHANGE events.

## References
- https://git.kernel.org/stable/c/5c2ca77212eb38559b0353b8363b7a84f4b019dd
- https://git.kernel.org/stable/c/5f33188457bbcc1b11ca87084037963c516ed3d9
- https://git.kernel.org/stable/c/af602c4d0ee548da18e2409b4b4da1079625a372
- https://git.kernel.org/stable/c/c0fbe31f6b20ade0465130685859faa5c86fda59
- https://git.kernel.org/stable/c/e16e960d55a40d36bd7c2494cc005e757dc9a1ef
- https://git.kernel.org/stable/c/f3c17ff65f54781cde696e16a6c577615ed735aa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74744.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74744
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
