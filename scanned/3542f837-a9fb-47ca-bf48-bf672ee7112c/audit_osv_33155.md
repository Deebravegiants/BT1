# [M] io_uring/kbuf: always use READ_ONCE() to read ring provided buffer lengths

## Summary
Severity: Medium
Advisory: CVE-2025-39816
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2025-39816
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.49, >=6.13.0 <6.16.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring/kbuf: always use READ_ONCE() to read ring provided buffer lengths

Since the buffers are mapped from userspace, it is prudent to use
READ_ONCE() to read the value into a local variable, and use that for
any other actions taken. Having a stable read of the buffer length
avoids worrying about it changing after checking, or being read multiple
times.

Similarly, the buffer may well change in between it being picked and
being committed. Ensure the looping for incremental ring buffer commit
stops if it hits a zero sized buffer, as no further progress can be made
at that point.

## References
- https://git.kernel.org/stable/c/390a61d284e1ced088d43928dfcf6f86fffdd780
- https://git.kernel.org/stable/c/695673eb5711ee5eb1769481cf1503714716a7d1
- https://git.kernel.org/stable/c/91f262ea2a76a02d9e37dba6637cfe6feebb20a8
- https://git.kernel.org/stable/c/98b6fa62c84f2e129161e976a5b9b3cb4ccd117b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39816.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39816
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
