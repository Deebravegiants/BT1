# [H] ksmbd: Fix the missing xa_store error check

## Summary
Severity: High
Advisory: CVE-2024-50284
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50284
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.117, >=6.2.0 <6.6.61, >=6.3.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: Fix the missing xa_store error check

xa_store() can fail, it return xa_err(-EINVAL) if the entry cannot
be stored in an XArray, or xa_err(-ENOMEM) if memory allocation failed,
so check error for xa_store() to fix it.

## References
- https://git.kernel.org/stable/c/3abab905b14f4ba756d413f37f1fb02b708eee93
- https://git.kernel.org/stable/c/726c1568b9145fa13ee248df184b186c382a7ff8
- https://git.kernel.org/stable/c/c2a232c4f790f4bcd4d218904c56ac7a39a448f5
- https://git.kernel.org/stable/c/d8664ce789bd46290c59a00da6897252f92c237d
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50284.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50284
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
