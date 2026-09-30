# [M] net: wwan: mhi: fix memory leak in mhi_mbim_dellink

## Summary
Severity: Medium
Advisory: CVE-2022-49866
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49866
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.79, >=5.16.0 <6.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: wwan: mhi: fix memory leak in mhi_mbim_dellink

MHI driver registers network device without setting the
needs_free_netdev flag, and does NOT call free_netdev() when
unregisters network device, which causes a memory leak.

This patch sets needs_free_netdev to true when registers
network device, which makes netdev subsystem call free_netdev()
automatically after unregister_netdevice().

## References
- https://git.kernel.org/stable/c/2845bc9070cef0c651987487d84d4813d64675dd
- https://git.kernel.org/stable/c/3cd3ffe952f78ec5dadf300cb58d4b38a0c0106d
- https://git.kernel.org/stable/c/668205b9c9f94d5ed6ab00cce9a46a654c2b5d16
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49866.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49866
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
