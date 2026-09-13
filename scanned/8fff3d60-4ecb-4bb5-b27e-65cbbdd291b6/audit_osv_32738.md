# [H] ksmbd: fix WARNING "do not call blocking ops when !TASK_RUNNING"

## Summary
Severity: High
Advisory: CVE-2025-37802
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-08
Source: https://osv.dev/vulnerability/CVE-2025-37802
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.12.26, >=6.13.0 <6.14.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix WARNING "do not call blocking ops when !TASK_RUNNING"

wait_event_timeout() will set the state of the current
task to TASK_UNINTERRUPTIBLE, before doing the condition check. This
means that ksmbd_durable_scavenger_alive() will try to acquire the mutex
while already in a sleeping state. The scheduler warns us by giving
the following warning:

do not call blocking ops when !TASK_RUNNING; state=2 set at
 [<0000000061515a6f>] prepare_to_wait_event+0x9f/0x6c0
WARNING: CPU: 2 PID: 4147 at kernel/sched/core.c:10099 __might_sleep+0x12f/0x160

mutex lock is not needed in ksmbd_durable_scavenger_alive().

## References
- https://git.kernel.org/stable/c/1df0d4c616138784e033ad337961b6e1a6bcd999
- https://git.kernel.org/stable/c/8f805b3746d2f41702c77cba22f94f8415fadd1a
- https://git.kernel.org/stable/c/cd161198e091e8a62b9bd631be970ea9a87d2d6a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37802.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37802
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
