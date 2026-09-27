# [M] kernel/irq/irqdomain.c: fix memory leak with using debugfs_lookup()

## Summary
Severity: Medium
Advisory: CVE-2023-52936
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-52936
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.93, >=5.16.0 <6.1.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

kernel/irq/irqdomain.c: fix memory leak with using debugfs_lookup()

When calling debugfs_lookup() the result must have dput() called on it,
otherwise the memory will leak over time.  To make things simpler, just
call debugfs_lookup_and_remove() instead which handles all of the logic
at once.

## References
- https://git.kernel.org/stable/c/066ecbf1a53eb0b92b10c8df7808666be6ea5681
- https://git.kernel.org/stable/c/cf1c917bf1c761a557b26410024e90057646c049
- https://git.kernel.org/stable/c/d83d7ed260283560700d4034a80baad46620481b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52936.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52936
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
