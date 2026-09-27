# [M] media: ar0521: don't overflow when checking PLL values

## Summary
Severity: Medium
Advisory: CVE-2024-53081
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53081
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.117, >=6.2.0 <6.6.61, >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: ar0521: don't overflow when checking PLL values

The PLL checks are comparing 64 bit integers with 32 bit
ones, as reported by Coverity. Depending on the values of
the variables, this may underflow.

Fix it ensuring that both sides of the expression are u64.

## References
- https://git.kernel.org/stable/c/438d3085ba5b8b5bfa5290faa594e577f6ac9aa7
- https://git.kernel.org/stable/c/5e1523076acf95b4ea68d19b6f27e6891267cc24
- https://git.kernel.org/stable/c/97ed0c0332d5525653668b31acf62ff1e6b50784
- https://git.kernel.org/stable/c/a244b82d0ae60326901f2b50c15e3118298b7ecd
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53081.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53081
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
