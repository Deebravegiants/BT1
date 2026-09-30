# [M] powerpc/mm: Fix null-pointer dereference in pgtable_cache_add

## Summary
Severity: Medium
Advisory: CVE-2023-52607
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-06
Source: https://osv.dev/vulnerability/CVE-2023-52607
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.33 <4.19.307, >=4.20.0 <5.4.269, >=5.5.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.77, >=6.2.0 <6.6.16, >=6.7.0 <6.7.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

powerpc/mm: Fix null-pointer dereference in pgtable_cache_add

kasprintf() returns a pointer to dynamically allocated memory
which can be NULL upon failure. Ensure the allocation was successful
by checking the pointer validity.

## References
- https://git.kernel.org/stable/c/145febd85c3bcc5c74d87ef9a598fc7d9122d532
- https://git.kernel.org/stable/c/21e45a7b08d7cd98d6a53c5fc5111879f2d96611
- https://git.kernel.org/stable/c/aa28eecb43cac6e20ef14dfc50b8892c1fbcda5b
- https://git.kernel.org/stable/c/ac3ed969a40357b0542d20f096a6d43acdfa6cc7
- https://git.kernel.org/stable/c/d482d61025e303a2bef3733a011b6b740215cfa1
- https://git.kernel.org/stable/c/f46c8a75263f97bda13c739ba1c90aced0d3b071
- https://git.kernel.org/stable/c/f6781add1c311c17eff43e14c786004bbacf901e
- https://git.kernel.org/stable/c/ffd29dc45bc0355393859049f6becddc3ed08f74
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52607.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52607
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
