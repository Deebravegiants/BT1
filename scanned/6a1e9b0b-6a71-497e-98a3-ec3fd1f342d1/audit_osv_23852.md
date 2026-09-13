# [M] ipv4: Fix data-races around sysctl_fib_multipath_hash_fields.

## Summary
Severity: Medium
Advisory: CVE-2022-49576
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49576
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv4: Fix data-races around sysctl_fib_multipath_hash_fields.

While reading sysctl_fib_multipath_hash_fields, it can be changed
concurrently.  Thus, we need to add READ_ONCE() to its readers.

## References
- https://git.kernel.org/stable/c/36f5b86f309b3b11295d087cd7433f1c897caf94
- https://git.kernel.org/stable/c/548d6678c4a3d43667e59686665f8674b82440a3
- https://git.kernel.org/stable/c/8895a9c2ac76fb9d3922fed4fe092c8ec5e5cccc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49576.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49576
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
