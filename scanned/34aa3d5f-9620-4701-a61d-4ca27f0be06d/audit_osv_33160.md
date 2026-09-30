# [M] io_uring/kbuf: fix signedness in this_len calculation

## Summary
Severity: Medium
Advisory: CVE-2025-39822
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2025-39822
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.16.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring/kbuf: fix signedness in this_len calculation

When importing and using buffers, buf->len is considered unsigned.
However, buf->len is converted to signed int when committing. This can
lead to unexpected behavior if the buffer is large enough to be
interpreted as a negative value. Make min_t calculation unsigned.

## References
- https://git.kernel.org/stable/c/c64eff368ac676e8540344d27a3de47e0ad90d21
- https://git.kernel.org/stable/c/f4f411c068402c370c4f9a9d4950a97af97bbbb1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39822.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39822
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
