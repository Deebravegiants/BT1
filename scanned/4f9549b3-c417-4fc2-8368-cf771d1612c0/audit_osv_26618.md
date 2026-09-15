# [M] scsi: snic: Fix memory leak with using debugfs_lookup()

## Summary
Severity: Medium
Advisory: CVE-2023-53414
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53414
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.99, >=5.16.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: snic: Fix memory leak with using debugfs_lookup()

When calling debugfs_lookup() the result must have dput() called on it,
otherwise the memory will leak over time.  To make things simpler, just
call debugfs_lookup_and_remove() instead which handles all of the logic at
once.

## References
- https://git.kernel.org/stable/c/3dec769caf337c55814fbf79ec8c91a3cce23bf3
- https://git.kernel.org/stable/c/5a46d8bdaf03e8a4bb83f0c363326d9aa66cc122
- https://git.kernel.org/stable/c/995424f59ab52fb432b26ccb3abced63745ea041
- https://git.kernel.org/stable/c/ad0e4e2fab928477f74d742e6e77d79245d3d3e7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53414.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53414
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
