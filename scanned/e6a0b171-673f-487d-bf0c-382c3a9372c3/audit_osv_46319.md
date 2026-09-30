# [H] fs/ntfs3: Fix slab-out-of-bounds read in DeleteIndexEntryRoot

## Summary
Severity: High
Advisory: CVE-2026-45935
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45935
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: Fix slab-out-of-bounds read in DeleteIndexEntryRoot

In the 'DeleteIndexEntryRoot' case of the 'do_action' function, the
entry size ('esize') is retrieved from the log record without adequate
bounds checking.

Specifically, the code calculates the end of the entry ('e2') using:
    e2 = Add2Ptr(e1, esize);

It then calculates the size for memmove using 'PtrOffset(e2, ...)',
which subtracts the end pointer from the buffer limit. If 'esize' is
maliciously large, 'e2' exceeds the used buffer size. This results in
a negative offset which, when cast to size_t for memmove, interprets
as a massive unsigned integer, leading to a heap buffer overflow.

This commit adds a check to ensure that the entry size ('esize') strictly
fits within the remaining used space of the index header before performing
memory operations.

## References
- https://git.kernel.org/stable/c/36c03f7f177b34d51f1cf1d2304b1074607bf4b0
- https://git.kernel.org/stable/c/78942172d5bff4d4afed8674abc09cc560ce44a0
- https://git.kernel.org/stable/c/a584b9d1059b29e97e17c919274e9adfb846f2a0
- https://git.kernel.org/stable/c/b271c9cb85927210b1b799e55ee7f702d12b4336
- https://git.kernel.org/stable/c/b2bc7c44ed1779fc9eaab9a186db0f0d01439622
- https://git.kernel.org/stable/c/c065541b71b79874c83d418a9acd18ad5826339b
- https://git.kernel.org/stable/c/f3b437a4c3e022a1449658ae9f3dd34859894513
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45935.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45935
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
