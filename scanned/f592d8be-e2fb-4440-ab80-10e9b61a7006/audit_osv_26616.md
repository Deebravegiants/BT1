# [M] time/debug: Fix memory leak with using debugfs_lookup()

## Summary
Severity: Medium
Advisory: CVE-2023-53403
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53403
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.99, >=5.16.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

time/debug: Fix memory leak with using debugfs_lookup()

When calling debugfs_lookup() the result must have dput() called on it,
otherwise the memory will leak over time.  To make things simpler, just
call debugfs_lookup_and_remove() instead which handles all of the logic at
once.

## References
- https://git.kernel.org/stable/c/15cffd01ed80e3506e29ba9f441e2358413b7317
- https://git.kernel.org/stable/c/5b268d8abaec6cbd4bd70d062e769098d96670aa
- https://git.kernel.org/stable/c/b588b42d077ce93c98704b41003bcec6a564b738
- https://git.kernel.org/stable/c/dc39fbd865a9819db4b622f610ba17b2ebc294f4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53403.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53403
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
