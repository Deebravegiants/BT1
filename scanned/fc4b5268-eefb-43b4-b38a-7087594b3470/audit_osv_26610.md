# [M] modpost: fix off by one in is_executable_section()

## Summary
Severity: Medium
Advisory: CVE-2023-53397
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53397
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <4.14.322, >=4.15.0 <5.4.251, >=5.5.0 <5.10.188, >=5.11.0 <5.15.121, >=5.16.0 <6.1.39, >=6.2.0 <6.3.13, >=6.4.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

modpost: fix off by one in is_executable_section()

The > comparison should be >= to prevent an out of bounds array
access.

## References
- https://git.kernel.org/stable/c/02dc8e8bdbe4412cfcf17ee3873e63fa5a55b957
- https://git.kernel.org/stable/c/3a3f1e573a105328a2cca45a7cfbebabbf5e3192
- https://git.kernel.org/stable/c/5e0424cd8a44b5f480feb06753cdf4e1f248d148
- https://git.kernel.org/stable/c/7ee557590bac154d324de446d1cd0444988bd511
- https://git.kernel.org/stable/c/8b2e77050b91199453bf19d0517b047b7339a9e3
- https://git.kernel.org/stable/c/cade370efe2f9e2a79ea8587506ffe2b51ac6d2b
- https://git.kernel.org/stable/c/cb0cdca5c979bc34c27602e2039562932c2591a4
- https://git.kernel.org/stable/c/dd872d5576cc94528f427c7264c2c438928cc6d2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53397.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53397
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
