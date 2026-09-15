# [M] tcp: Fix data-races around sysctl_tcp_l3mdev_accept.

## Summary
Severity: Medium
Advisory: CVE-2022-49599
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49599
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.5.0 <5.10.137, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: Fix data-races around sysctl_tcp_l3mdev_accept.

While reading sysctl_tcp_l3mdev_accept, it can be changed concurrently.
Thus, we need to add READ_ONCE() to its readers.

## References
- https://git.kernel.org/stable/c/08a75f10679470552a3a443f9aefd1399604d31d
- https://git.kernel.org/stable/c/1d9c81833dec46ccb52a1d0db970fefb7c4fa071
- https://git.kernel.org/stable/c/7d38d86b818104cf88961f3aebea34da89364a8e
- https://git.kernel.org/stable/c/9ba9cd43b5776c27d25e5a32dde9e80bdeb1c6a1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49599.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49599
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
