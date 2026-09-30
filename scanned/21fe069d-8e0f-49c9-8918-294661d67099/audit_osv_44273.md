# [H] io_uring: preserve task restrictions across exec

## Summary
Severity: High
Advisory: CVE-2026-80713
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80713
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.0.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring: preserve task restrictions across exec

Per-task restrictions apply to all rings created by a task. Once
installed, they should not be dropped across exec.

For a task that has used io_uring, the exec cancellation path calls
__io_uring_free(). This frees both the task context and the per-task
restriction, so a ring created after exec is unrestricted.

Split task context cleanup into io_uring_free_tctx(), and use it from
the exec cancellation path. Keep __io_uring_free() for final task
cleanup, where both the context and restriction are released.

## References
- https://git.kernel.org/stable/c/bc0e8faf90e776a2f1f3967a04e8091e6bdb4977
- https://git.kernel.org/stable/c/fcef9325afeecced693a7438e975e4a3f8e2716f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80713.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80713
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
