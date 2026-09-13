# [M] staging: pi433: fix memory leak with using debugfs_lookup()

## Summary
Severity: Medium
Advisory: CVE-2023-53355
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2023-53355
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <6.1.18, >=6.2.0 <6.2.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

staging: pi433: fix memory leak with using debugfs_lookup()

When calling debugfs_lookup() the result must have dput() called on it,
otherwise the memory will leak over time.  To make things simpler, just
call debugfs_lookup_and_remove() instead which handles all of the logic
at once.  This requires saving off the root directory dentry to make
creation of individual device subdirectories easier.

## References
- https://git.kernel.org/stable/c/04f3cda40e9f6653ae15ed3fcf26ef2860f4df66
- https://git.kernel.org/stable/c/2f36e789e540df6a9fbf471b3a2ba62a8b361586
- https://git.kernel.org/stable/c/bb16f3102607b69e1a0233f4b73c6e337f86ef8d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53355.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53355
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
