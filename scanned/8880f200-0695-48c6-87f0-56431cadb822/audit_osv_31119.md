# [H] wifi: wcn36xx: fix channel survey memory allocation size

## Summary
Severity: High
Advisory: CVE-2024-57997
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-57997
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.129, >=6.2.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: wcn36xx: fix channel survey memory allocation size

KASAN reported a memory allocation issue in wcn->chan_survey
due to incorrect size calculation.
This commit uses kcalloc to allocate memory for wcn->chan_survey,
ensuring proper initialization and preventing the use of uninitialized
values when there are no frames on the channel.

## References
- https://git.kernel.org/stable/c/34cd2817708aec51ef1a6c007e0d6d5342a025d7
- https://git.kernel.org/stable/c/6200d947f050efdba4090dfefd8a01981363d954
- https://git.kernel.org/stable/c/64c4dcaeac1dc1030e47883b04a617ca9a4f164e
- https://git.kernel.org/stable/c/ae68efdff7a7a42ab251cac79d8713de6f0dbaa0
- https://git.kernel.org/stable/c/e95f9c408ff8311f75eeabc8acf34a66670d8815
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57997.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57997
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
