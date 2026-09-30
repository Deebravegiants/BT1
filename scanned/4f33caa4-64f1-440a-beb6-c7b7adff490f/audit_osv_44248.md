# [C] perf sched: Fix register_pid() overflow, strcpy, and BUG_ON

## Summary
Severity: Critical
Advisory: CVE-2026-80671
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80671
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.32 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

perf sched: Fix register_pid() overflow, strcpy, and BUG_ON

register_pid() has several issues when processing untrusted perf.data:

1. Integer overflow: (pid + 1) * sizeof(struct task_desc *) can wrap
   to a small value on 32-bit systems when pid is large (e.g.
   0x40000000), causing realloc to return a tiny buffer followed by
   out-of-bounds writes in the initialization loop.

2. Heap buffer overflow: strcpy(task->comm, comm) copies the
   untrusted comm string into a fixed 20-byte COMM_LEN buffer with
   no length check.

3. BUG_ON on allocation failure: perf.data is untrusted input, so
   allocation failures should be handled gracefully rather than
   killing the process.

4. Realloc of sched->tasks assigned directly back, leaking the old
   pointer on failure; nr_tasks incremented before the realloc,
   leaving corrupted state on failure.

Cap pid at PID_MAX_LIMIT (4194304, matching the kernel's maximum
on 64-bit), replace strcpy with strlcpy, guard against NULL comm,
replace BUG_ON with NULL returns using safe realloc patterns, and
add NULL checks in callers that dereference the result.

## References
- https://git.kernel.org/stable/c/5949d339f5ec98752d56dcd4e36f619a59d513a5
- https://git.kernel.org/stable/c/5ea1dcc9418c4e06ce29ed5170596f497ba86872
- https://git.kernel.org/stable/c/652cea73b7b7b7c622a2be670e44e3c499c6d49f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80671.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80671
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
