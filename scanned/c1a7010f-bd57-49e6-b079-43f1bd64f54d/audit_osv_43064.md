# [H] net: sungem: fix probe error cleanup

## Summary
Severity: High
Advisory: CVE-2026-72406
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72406
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: sungem: fix probe error cleanup

gem_init_one() calls gem_remove_one() when register_netdev() fails.
gem_remove_one() unregisters and frees resources owned by the net_device,
including the DMA block, MMIO mapping, PCI regions, and the net_device
itself. gem_init_one() then falls through to its own cleanup labels and
frees the same resources again.

Keep the register_netdev() error path in gem_init_one(): clear drvdata so
PM/remove paths do not see a half-registered device, remove the NAPI
instance added during probe, and let the existing cleanup labels release
the resources once.

The issue was found by a local static-analysis checker for probe error
paths. The reported path was manually inspected before sending this fix.

Compile-tested with CONFIG_SUNGEM=y. Runtime testing was not performed
because no sungem hardware is available.

## References
- https://git.kernel.org/stable/c/331c99029a1cee1111f82f63d15b3cdebefbd341
- https://git.kernel.org/stable/c/36dea2f639249460d13f6ca66b2a9064187cd34d
- https://git.kernel.org/stable/c/a63eaf7605d1579cf3f551792e478cfaf5ac37d1
- https://git.kernel.org/stable/c/b15a3cc68e2450aa0edd94a74a7bdd45fcc17dd9
- https://git.kernel.org/stable/c/bc49e8746584564dba47d963d1916cc876fc6f6b
- https://git.kernel.org/stable/c/f1d04fefb0c2a2de32d9cee22cdc2088be3758d1
- https://git.kernel.org/stable/c/f3bd60b26814b7c3c57c629abb0857dfc76d214a
- https://git.kernel.org/stable/c/fb73cdc50b6755e5c3a80a195b2708a39ada0230
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72406.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72406
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
