# [H] netfilter: nft_chain_filter: handle NETDEV_UNREGISTER for inet/ingress basechain

## Summary
Severity: High
Advisory: CVE-2024-26808
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-04
Source: https://osv.dev/vulnerability/CVE-2024-26808
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.76, >=6.2.0 <6.6.15, >=6.7.0 <6.7.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nft_chain_filter: handle NETDEV_UNREGISTER for inet/ingress basechain

Remove netdevice from inet/ingress basechain in case NETDEV_UNREGISTER
event is reported, otherwise a stale reference to netdevice remains in
the hook list.

## References
- https://git.kernel.org/stable/c/01acb2e8666a6529697141a6017edbf206921913
- https://git.kernel.org/stable/c/36a0a80f32209238469deb481967d777a3d539ee
- https://git.kernel.org/stable/c/70f17b48c86622217a58d5099d29242fc9adac58
- https://git.kernel.org/stable/c/9489e214ea8f2a90345516016aa51f2db3a8cc2f
- https://git.kernel.org/stable/c/af149a46890e8285d1618bd68b8d159bdb87fdb3
- https://git.kernel.org/stable/c/e5888acbf1a3d8d021990ce6c6061fd5b2bb21b4
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26808.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26808
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
