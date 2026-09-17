# [H] gve: prevent ethtool ops after shutdown

## Summary
Severity: High
Advisory: CVE-2025-38735
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-38735
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.1.149, >=6.2.0 <6.6.103, >=6.7.0 <6.12.44, >=6.13.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

gve: prevent ethtool ops after shutdown

A crash can occur if an ethtool operation is invoked
after shutdown() is called.

shutdown() is invoked during system shutdown to stop DMA operations
without performing expensive deallocations. It is discouraged to
unregister the netdev in this path, so the device may still be visible
to userspace and kernel helpers.

In gve, shutdown() tears down most internal data structures. If an
ethtool operation is dispatched after shutdown(), it will dereference
freed or NULL pointers, leading to a kernel panic. While graceful
shutdown normally quiesces userspace before invoking the reboot
syscall, forced shutdowns (as observed on GCP VMs) can still trigger
this path.

Fix by calling netif_device_detach() in shutdown().
This marks the device as detached so the ethtool ioctl handler
will skip dispatching operations to the driver.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://git.kernel.org/stable/c/48a4e89d50e8ea52e800bc7865970b92fcf4647c
- https://git.kernel.org/stable/c/75a9a46d67f46d608205888f9b34e315c1786345
- https://git.kernel.org/stable/c/9d8a41e9a4ff83ff666de811e7f012167cdc00e9
- https://git.kernel.org/stable/c/a7efffeecb881b4649fdc30de020ef910f35d646
- https://git.kernel.org/stable/c/ba51d73408edf815cbaeab148625576c2dd90192
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38735.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38735
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
