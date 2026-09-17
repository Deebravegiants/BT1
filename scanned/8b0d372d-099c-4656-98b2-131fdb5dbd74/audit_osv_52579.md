# [M] CVE-2021-47601

## Summary
Severity: Medium
Advisory: CVE-2021-47601
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2021-47601
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

tee: amdtee: fix an IS_ERR() vs NULL bug

The __get_free_pages() function does not return error pointers it returns
NULL so fix this condition to avoid a NULL dereference.

## References
- https://git.kernel.org/stable/c/640e28d618e82be78fb43b4bf5113bc90d6aa442
- https://git.kernel.org/stable/c/832f3655c6138c23576ed268e31cc76e0f05f2b1
- https://git.kernel.org/stable/c/9d7482771fac8d8e38e763263f2ca0ca12dd22c6
