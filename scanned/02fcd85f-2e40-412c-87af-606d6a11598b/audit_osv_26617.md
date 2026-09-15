# [M] trace/blktrace: fix memory leak with using debugfs_lookup()

## Summary
Severity: Medium
Advisory: CVE-2023-53408
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53408
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.99, >=5.16.0 <6.1.16, >=5.17.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

trace/blktrace: fix memory leak with using debugfs_lookup()

When calling debugfs_lookup() the result must have dput() called on it,
otherwise the memory will leak over time.  To make things simpler, just
call debugfs_lookup_and_remove() instead which handles all of the logic
at once.

## References
- https://git.kernel.org/stable/c/3036f5f5ae5210797d95446795df01c1249af9ad
- https://git.kernel.org/stable/c/5286b72fb425291af5f4ca7285d73c16a08d8691
- https://git.kernel.org/stable/c/83e8864fee26f63a7435e941b7c36a20fd6fe93e
- https://git.kernel.org/stable/c/a2e4b48d6f9b39aa19bafe223f9dd436a692fc80
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53408.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53408
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
