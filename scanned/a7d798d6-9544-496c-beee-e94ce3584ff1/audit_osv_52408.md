# [M] CVE-2021-47417

## Summary
Severity: Medium
Advisory: CVE-2021-47417
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47417
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

libbpf: Fix memory leak in strset

Free struct strset itself, not just its internal parts.

## References
- https://git.kernel.org/stable/c/9e8e7504e09831c469b67d6dc11d9a72654bdb8c
- https://git.kernel.org/stable/c/b0e875bac0fab3e7a7431c2eee36a8ccc0c712ac
