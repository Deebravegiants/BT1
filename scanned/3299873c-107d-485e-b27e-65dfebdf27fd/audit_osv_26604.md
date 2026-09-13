# [M] drivers: base: dd: fix memory leak with using debugfs_lookup()

## Summary
Severity: Medium
Advisory: CVE-2023-53390
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53390
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.100, >=5.16.0 <6.1.18, >=6.2.0 <6.2.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drivers: base: dd: fix memory leak with using debugfs_lookup()

When calling debugfs_lookup() the result must have dput() called on it,
otherwise the memory will leak over time.  To make things simpler, just
call debugfs_lookup_and_remove() instead which handles all of the logic
at once.

## References
- https://git.kernel.org/stable/c/36c893d3a759ae7c91ee7d4871ebfc7504f08c40
- https://git.kernel.org/stable/c/5a7a9efdb193d3c8a35821548a8e99612c358828
- https://git.kernel.org/stable/c/7f1e53f88e8babf293ec052b70aa9d2a3554360c
- https://git.kernel.org/stable/c/8e47e2bf78812adbd73c45c941d3c51add30b58d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53390.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53390
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
