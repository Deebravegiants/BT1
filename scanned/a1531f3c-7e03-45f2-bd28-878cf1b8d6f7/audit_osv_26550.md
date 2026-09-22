# [M] USB: chipidea: fix memory leak with using debugfs_lookup()

## Summary
Severity: Medium
Advisory: CVE-2023-53334
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53334
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.100, >=5.16.0 <6.1.18, >=6.2.0 <6.2.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

USB: chipidea: fix memory leak with using debugfs_lookup()

When calling debugfs_lookup() the result must have dput() called on it,
otherwise the memory will leak over time.  To make things simpler, just
call debugfs_lookup_and_remove() instead which handles all of the logic
at once.

## References
- https://git.kernel.org/stable/c/4322661af6d7a586a5798ab9aa443f49895b6943
- https://git.kernel.org/stable/c/610373dd354f3d393aa3bdcab59f55024c16b5e5
- https://git.kernel.org/stable/c/972e0682f6e3ee6ecf002657df4aaa511d51dd6c
- https://git.kernel.org/stable/c/ff35f3ea3baba5b81416ac02d005cfbf6dd182fa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53334.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53334
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
