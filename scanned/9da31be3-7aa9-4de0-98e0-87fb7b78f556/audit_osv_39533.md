# [H] mm/vmalloc: take vmap_purge_lock in shrinker

## Summary
Severity: High
Advisory: CVE-2026-46093
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46093
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.96, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/vmalloc: take vmap_purge_lock in shrinker

decay_va_pool_node() can be invoked concurrently from two paths:
__purge_vmap_area_lazy() when pools are being purged, and the shrinker via
vmap_node_shrink_scan().

However, decay_va_pool_node() is not safe to run concurrently, and the
shrinker path currently lacks serialization, leading to races and possible
leaks.

Protect decay_va_pool_node() by taking vmap_purge_lock in the shrinker
path to ensure serialization with purge users.

## References
- https://git.kernel.org/stable/c/12f2341b4c235d5593a433abac201c1c6725787f
- https://git.kernel.org/stable/c/687ccdf582169cd680aeaf24cc953807c4cd4345
- https://git.kernel.org/stable/c/c15ff206ba78820bf2873d0c668a882e99f4b631
- https://git.kernel.org/stable/c/ec05f51f1e65bce95528543eb73fda56fd201d94
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46093.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46093
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
