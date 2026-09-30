# [H] scsi: mpi3mr: Synchronous access b/w reset and tm thread for reply queue

## Summary
Severity: High
Advisory: CVE-2025-37861
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-09
Source: https://osv.dev/vulnerability/CVE-2025-37861
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <6.12.24, >=6.13.0 <6.13.12, >=6.14.0 <6.14.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: mpi3mr: Synchronous access b/w reset and tm thread for reply queue

When the task management thread processes reply queues while the reset
thread resets them, the task management thread accesses an invalid queue ID
(0xFFFF), set by the reset thread, which points to unallocated memory,
causing a crash.

Add flag 'io_admin_reset_sync' to synchronize access between the reset,
I/O, and admin threads. Before a reset, the reset handler sets this flag to
block I/O and admin processing threads. If any thread bypasses the initial
check, the reset thread waits up to 10 seconds for processing to finish. If
the wait exceeds 10 seconds, the controller is marked as unrecoverable.

## References
- https://git.kernel.org/stable/c/65ba18c84dbd03afe9b38c06c151239d97a09834
- https://git.kernel.org/stable/c/75b67dca4195e11ccf966a704787b2aa2754a457
- https://git.kernel.org/stable/c/8d310d66e2b0f5f9f709764641647e8a3a4924fa
- https://git.kernel.org/stable/c/f195fc060c738d303a21fae146dbf85e1595fb4c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37861.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37861
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
