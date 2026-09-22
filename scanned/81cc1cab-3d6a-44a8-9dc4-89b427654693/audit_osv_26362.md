# [M] HV: hv_balloon: fix memory leak with using debugfs_lookup()

## Summary
Severity: Medium
Advisory: CVE-2023-52937
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-52937
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

HV: hv_balloon: fix memory leak with using debugfs_lookup()

When calling debugfs_lookup() the result must have dput() called on it,
otherwise the memory will leak over time.  To make things simpler, just
call debugfs_lookup_and_remove() instead which handles all of the logic
at once.

## References
- https://git.kernel.org/stable/c/0b570a059cf42ad6e2eb632f47c23813d58d8303
- https://git.kernel.org/stable/c/6dfb0771429a63db8561d44147f2bb76f93e1c86
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52937.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52937
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
