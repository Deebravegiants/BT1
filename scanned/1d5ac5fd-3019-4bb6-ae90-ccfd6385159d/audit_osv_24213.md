# [H] scsi: libsas: Fix use-after-free bug in smp_execute_task_sg()

## Summary
Severity: High
Advisory: CVE-2022-50422
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2022-50422
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.19 <5.4.220, >=5.5.0 <5.10.150, >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: libsas: Fix use-after-free bug in smp_execute_task_sg()

When executing SMP task failed, the smp_execute_task_sg() calls del_timer()
to delete "slow_task->timer". However, if the timer handler
sas_task_internal_timedout() is running, the del_timer() in
smp_execute_task_sg() will not stop it and a UAF will happen. The process
is shown below:

      (thread 1)               |        (thread 2)
smp_execute_task_sg()          | sas_task_internal_timedout()
 ...                           |
 del_timer()                   |
 ...                           |  ...
 sas_free_task(task)           |
  kfree(task->slow_task) //FREE|
                               |  task->slow_task->... //USE

Fix by calling del_timer_sync() in smp_execute_task_sg(), which makes sure
the timer handler have finished before the "task->slow_task" is
deallocated.

## References
- https://git.kernel.org/stable/c/117331a2a5227fb4369c2a1f321d3e3e2e2ef8fe
- https://git.kernel.org/stable/c/2e12ce270f0d926085c1209cc90397e307deef97
- https://git.kernel.org/stable/c/46ba53c30666717cb06c2b3c5d896301cd00d0c0
- https://git.kernel.org/stable/c/a9e5176ead6de64f572ad5c87a72825d9d3c82ae
- https://git.kernel.org/stable/c/e45a1516d2933703a4823d9db71e17c3abeba24f
- https://git.kernel.org/stable/c/f7a785177611ffc97d645fcbc196e6de6ad2421d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50422.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50422
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
