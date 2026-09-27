# [H] ALSA: compress: Fix task creation error unwind

## Summary
Severity: High
Advisory: CVE-2026-64485
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64485
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: compress: Fix task creation error unwind

snd_compr_task_new() allocates the driver task before validating the
returned DMA buffers and reserving file descriptors. When either of
those later steps fails, the core frees its task wrapper and DMA-buffer
references without calling the driver's task_free() callback. Any
driver resources allocated by task_create() are therefore leaked.

The dual-fd allocation path also jumps to cleanup without storing the
negative get_unused_fd_flags() result in retval. Since retval still
contains the successful task_create() return value, TASK_CREATE can
incorrectly report success although the task was discarded.

Preserve the fd allocation errors and call task_free() when failure
occurs after a successful task_create() callback.

## References
- https://git.kernel.org/stable/c/426a9947a38d272d0e19c031658da68e31128667
- https://git.kernel.org/stable/c/4a60127debb9e370d6c0e22a307326b624a141f3
- https://git.kernel.org/stable/c/b27a75d42044d9d4709095617730b91b1c4af423
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64485.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64485
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
