# [H] sh: push-switch: Reorder cleanup operations to avoid use-after-free bug

## Summary
Severity: High
Advisory: CVE-2023-52629
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-29
Source: https://osv.dev/vulnerability/CVE-2023-52629
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.20 <6.5.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

sh: push-switch: Reorder cleanup operations to avoid use-after-free bug

The original code puts flush_work() before timer_shutdown_sync()
in switch_drv_remove(). Although we use flush_work() to stop
the worker, it could be rescheduled in switch_timer(). As a result,
a use-after-free bug can occur. The details are shown below:

      (cpu 0)                    |      (cpu 1)
switch_drv_remove()              |
 flush_work()                    |
  ...                            |  switch_timer // timer
                                 |   schedule_work(&psw->work)
 timer_shutdown_sync()           |
 ...                             |  switch_work_handler // worker
 kfree(psw) // free              |
                                 |   psw->state = 0 // use

This patch puts timer_shutdown_sync() before flush_work() to
mitigate the bugs. As a result, the worker and timer will be
stopped safely before the deallocate operations.

## References
- https://git.kernel.org/stable/c/246f80a0b17f8f582b2c0996db02998239057c65
- https://git.kernel.org/stable/c/610dbd8ac271aa36080aac50b928d700ee3fe4de
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52629.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52629
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
