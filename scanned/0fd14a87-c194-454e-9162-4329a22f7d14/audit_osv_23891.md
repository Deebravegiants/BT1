# [M] nexthop: Fix data-races around nexthop_compat_mode.

## Summary
Severity: Medium
Advisory: CVE-2022-49629
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49629
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.132, >=5.11.0 <5.15.56, >=5.16.0 <5.18.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

nexthop: Fix data-races around nexthop_compat_mode.

While reading nexthop_compat_mode, it can be changed concurrently.
Thus, we need to add READ_ONCE() to its readers.

## References
- https://git.kernel.org/stable/c/0d17723afea3ae8c9f245c9bbd2ba5945b77e812
- https://git.kernel.org/stable/c/a51040d4b120f3520df64fb0b9c63b31d69bea9b
- https://git.kernel.org/stable/c/ae3054f6fbccc90f14ecd6cf9b2c09a2401c64fd
- https://git.kernel.org/stable/c/bdf00bf24bef9be1ca641a6390fd5487873e0d2e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49629.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49629
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
