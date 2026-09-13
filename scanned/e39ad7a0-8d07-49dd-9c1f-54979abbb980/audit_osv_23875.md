# [M] ip: Fix a data-race around sysctl_fwmark_reflect.

## Summary
Severity: Medium
Advisory: CVE-2022-49602
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49602
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.16.0 <4.9.325, >=4.10.0 <4.14.290, >=4.15.0 <4.19.254, >=4.20.0 <5.4.208, >=5.5.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

ip: Fix a data-race around sysctl_fwmark_reflect.

While reading sysctl_fwmark_reflect, it can be changed concurrently.
Thus, we need to add READ_ONCE() to its reader.

## References
- https://git.kernel.org/stable/c/0ee76fe01ff3c0b4efaa500aecc90d7c8d3a8860
- https://git.kernel.org/stable/c/25a635a67c830766110410fea88ec4e6ee29684b
- https://git.kernel.org/stable/c/5e7a1be3e68deef250ad43cc91f7bb8d7d758b48
- https://git.kernel.org/stable/c/85d0b4dbd74b95cc492b1f4e34497d3f894f5d9a
- https://git.kernel.org/stable/c/9096edcf4854289f92252e086cf6e498c7f8c21d
- https://git.kernel.org/stable/c/a475ecc9ad919aa3ebdd4e4a6ee612b793bf74b3
- https://git.kernel.org/stable/c/dccf8a67f30e18980d13f07006e5a536bbd1e136
- https://git.kernel.org/stable/c/fc92e3b4bebfdd986ef1d2c5019f236837b0b982
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49602.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49602
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
