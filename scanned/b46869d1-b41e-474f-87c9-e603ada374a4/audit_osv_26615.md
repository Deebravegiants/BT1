# [M] kernel/printk/index.c: fix memory leak with using debugfs_lookup()

## Summary
Severity: Medium
Advisory: CVE-2023-53402
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53402
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.100, >=5.16.0 <6.1.18, >=6.2.0 <6.2.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

kernel/printk/index.c: fix memory leak with using debugfs_lookup()

When calling debugfs_lookup() the result must have dput() called on it,
otherwise the memory will leak over time.  To make things simpler, just
call debugfs_lookup_and_remove() instead which handles all of the logic
at once.

## References
- https://git.kernel.org/stable/c/13969236b6900b5a3625ad2193569588e978f1cc
- https://git.kernel.org/stable/c/2e07fa2e30d48d24a791483774a3d4b76769e0cf
- https://git.kernel.org/stable/c/55bf243c514553e907efcf2bda92ba090eca8c64
- https://git.kernel.org/stable/c/c578a68ffcdc2e8c72556bebdaae2b7500398e81
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53402.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53402
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
