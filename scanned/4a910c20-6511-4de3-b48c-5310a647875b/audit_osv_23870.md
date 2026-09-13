# [M] tcp: Fix data-races around sysctl_tcp_base_mss.

## Summary
Severity: Medium
Advisory: CVE-2022-49597
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49597
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.17 <5.4.208, >=5.5.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: Fix data-races around sysctl_tcp_base_mss.

While reading sysctl_tcp_base_mss, it can be changed concurrently.
Thus, we need to add READ_ONCE() to its readers.

## References
- https://git.kernel.org/stable/c/30b73edc1d2459ba2c71cb58fbf84a1a6e640fbf
- https://git.kernel.org/stable/c/4d7dea651b7fe0322be95054f64e3711afccc543
- https://git.kernel.org/stable/c/514d2254c7b8aa2d257f5ffc79f0d96be2d6bfda
- https://git.kernel.org/stable/c/88d78bc097cd8ebc6541e93316c9d9bf651b13e8
- https://git.kernel.org/stable/c/9ca18116bc16ec31b9a3ce28ea1350badfa36128
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49597.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49597
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
