# [H] RDMA/restrack: Release MR restrack when delete

## Summary
Severity: High
Advisory: CVE-2022-50822
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2022-50822
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/restrack: Release MR restrack when delete

The MR restrack also needs to be released when delete it, otherwise it
cause memory leak as the task struct won't be released.

## References
- https://git.kernel.org/stable/c/13586753ae55146269a6dc8b216f17d86b81560c
- https://git.kernel.org/stable/c/37c90753079fc95d93cc31b79796dd2ae57ad018
- https://git.kernel.org/stable/c/8731cb5c7820bef577bab4ff17691fbf61c671cb
- https://git.kernel.org/stable/c/dac153f2802db1ad46207283cb9b2aae3d707a45
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50822.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50822
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
