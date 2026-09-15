# [M] ipv4: Fix data-races around sysctl_fib_multipath_hash_policy.

## Summary
Severity: Medium
Advisory: CVE-2022-49579
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49579
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv4: Fix data-races around sysctl_fib_multipath_hash_policy.

While reading sysctl_fib_multipath_hash_policy, it can be changed
concurrently.  Thus, we need to add READ_ONCE() to its readers.

## References
- https://git.kernel.org/stable/c/21fb844bc1dc1461f5038d655aa1a14f39e13049
- https://git.kernel.org/stable/c/7998c12a08c97cc26660532c9f90a34bd7d8da5a
- https://git.kernel.org/stable/c/918ee6592ab9a2ff5316d06cfd4aaef60ccabec6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49579.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49579
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
