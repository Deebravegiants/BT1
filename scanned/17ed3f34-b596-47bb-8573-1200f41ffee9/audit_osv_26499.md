# [M] misc: vmw_balloon: fix memory leak with using debugfs_lookup()

## Summary
Severity: Medium
Advisory: CVE-2023-53279
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53279
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.100, >=5.16.0 <6.1.18, >=6.2.0 <6.2.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

misc: vmw_balloon: fix memory leak with using debugfs_lookup()

When calling debugfs_lookup() the result must have dput() called on it,
otherwise the memory will leak over time.  To make things simpler, just
call debugfs_lookup_and_remove() instead which handles all of the logic at
once.

## References
- https://git.kernel.org/stable/c/209cdbd07cfaa4b7385bad4eeb47e5ec1887d33d
- https://git.kernel.org/stable/c/b94b39bf3d545671f210a2257d18e33c8b874699
- https://git.kernel.org/stable/c/d1c545e44c1ec08bef0c0c14e632eec516431e9c
- https://git.kernel.org/stable/c/f7651fa88b17c2d7af949981a2423179db5e9453
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53279.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53279
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
