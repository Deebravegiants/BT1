# [C] vxlan: use neigh_ha_snapshot() in route_shortcircuit()

## Summary
Severity: Critical
Advisory: CVE-2026-74475
Ecosystem: Linux
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:L)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74475
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

vxlan: use neigh_ha_snapshot() in route_shortcircuit()

The neighbour hardware address n->ha can be updated asynchronously by the
neighbour subsystem, protected by n->ha_lock seqlock. Reading n->ha without
holding the seqlock loop can lead to torn reads or reading a partially updated
MAC address.

Use neigh_ha_snapshot() in route_shortcircuit() to safely copy n->ha under
read_seqbegin()/read_seqretry() lock protection before using it.

Note that arp_reduce() and neigh_reduce() seem to have the same issue
left for future patches.

## References
- https://git.kernel.org/stable/c/05f2987f73daa05333fd713d05546142f9f7c5f0
- https://git.kernel.org/stable/c/32a9590a8d30426e3db63e6b20893e47e02576c0
- https://git.kernel.org/stable/c/87210054bad82bbae6f483a742dc45722fb47a6b
- https://git.kernel.org/stable/c/8eca411347e1d38964f9ed2c8d3b6ab0e7e4473d
- https://git.kernel.org/stable/c/d08e8ac13f2e228cc7fc3c70b5ebe71557b624a0
- https://git.kernel.org/stable/c/d0993fc053f29e15cc7c9fe2029df3882a2ab5ab
- https://git.kernel.org/stable/c/ec341bb76d77b4c2948764375ee6bfeef4bb41c3
- https://git.kernel.org/stable/c/ff89415d34c3ab9f5312316423122e664ed3524f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74475.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74475
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
