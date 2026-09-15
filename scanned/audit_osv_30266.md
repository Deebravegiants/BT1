# [M] netdevsim: Add trailing zero to terminate the string in nsim_nexthop_bucket_activity_write()

## Summary
Severity: Medium
Advisory: CVE-2024-50259
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-09
Source: https://osv.dev/vulnerability/CVE-2024-50259
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.171, >=5.16.0 <6.1.116, >=6.2.0 <6.6.60, >=6.7.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

netdevsim: Add trailing zero to terminate the string in nsim_nexthop_bucket_activity_write()

This was found by a static analyzer.
We should not forget the trailing zero after copy_from_user()
if we will further do some string operations, sscanf() in this
case. Adding a trailing zero will ensure that the function
performs properly.

## References
- https://git.kernel.org/stable/c/27bd7a742e171362c9eb52ad5d1d71d3321f949f
- https://git.kernel.org/stable/c/4ce1f56a1eaced2523329bef800d004e30f2f76c
- https://git.kernel.org/stable/c/6a604877160fe5ab2e1985d5ce1ba6a61abe0693
- https://git.kernel.org/stable/c/bcba86e03b3aac361ea671672cf48eed11f9011c
- https://git.kernel.org/stable/c/c2150f666c6fc301d5d1643ed0f92251f1a0ff0d
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50259.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50259
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
