# [M] tcp: Fix a data-race around sysctl_tcp_probe_threshold.

## Summary
Severity: Medium
Advisory: CVE-2022-49595
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49595
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <4.9.325, >=4.10.0 <4.14.290, >=4.15.0 <4.19.254, >=4.20.0 <5.4.208, >=5.5.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: Fix a data-race around sysctl_tcp_probe_threshold.

While reading sysctl_tcp_probe_threshold, it can be changed concurrently.
Thus, we need to add READ_ONCE() to its reader.

## References
- https://git.kernel.org/stable/c/44768749980d53bc01980d9c060f736808d11af0
- https://git.kernel.org/stable/c/92c0aa4175474483d6cf373314343d4e624e882a
- https://git.kernel.org/stable/c/96900fa61777402eb5056269d8000aace33a8b6c
- https://git.kernel.org/stable/c/9b5dc7ad6da1373d3c60d4b869d688f996e5d219
- https://git.kernel.org/stable/c/b04817c94fbd285a967d9b830b274fe9998c9c0b
- https://git.kernel.org/stable/c/d452ce36f2d4c402fa3f5275c9677f80166e7fc6
- https://git.kernel.org/stable/c/f524c3e7f6cdad66b3b6a912cef47b656f8b0de3
- https://git.kernel.org/stable/c/fa5fb2cf9393db898772db8cb897ed5fd265eb78
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49595.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49595
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
