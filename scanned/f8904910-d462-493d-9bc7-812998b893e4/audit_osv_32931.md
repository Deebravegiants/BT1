# [H] posix-cpu-timers: fix race between handle_posix_cpu_timers() and posix_cpu_timer_del()

## Summary
Severity: High
Advisory: CVE-2025-38352
Aliases: A-425282960, ASB-A-425282960
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-22
Source: https://osv.dev/vulnerability/CVE-2025-38352
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.36 <5.4.295, >=5.5.0 <5.10.239, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.94, >=6.7.0 <6.12.34, >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

posix-cpu-timers: fix race between handle_posix_cpu_timers() and posix_cpu_timer_del()

If an exiting non-autoreaping task has already passed exit_notify() and
calls handle_posix_cpu_timers() from IRQ, it can be reaped by its parent
or debugger right after unlock_task_sighand().

If a concurrent posix_cpu_timer_del() runs at that moment, it won't be
able to detect timer->it.cpu.firing != 0: cpu_timer_task_rcu() and/or
lock_task_sighand() will fail.

Add the tsk->exit_state check into run_posix_cpu_timers() to fix this.

This fix is not needed if CONFIG_POSIX_CPU_TIMERS_TASK_WORK=y, because
exit_task_work() is called before exit_notify(). But the check still
makes sense, task_work_add(&tsk->posix_cputimers_work.work) will fail
anyway in this case.

## References
- https://git.kernel.org/stable/c/2c72fe18cc5f9f1750f5bc148cf1c94c29e106ff
- https://git.kernel.org/stable/c/2f3daa04a9328220de46f0d5c919a6c0073a9f0b
- https://git.kernel.org/stable/c/460188bc042a3f40f72d34b9f7fc6ee66b0b757b
- https://git.kernel.org/stable/c/764a7a5dfda23f69919441f2eac2a83e7db6e5bb
- https://git.kernel.org/stable/c/78a4b8e3795b31dae58762bc091bb0f4f74a2200
- https://git.kernel.org/stable/c/c076635b3a42771ace7d276de8dc3bc76ee2ba1b
- https://git.kernel.org/stable/c/c29d5318708e67ac13c1b6fc1007d179fb65b4d7
- https://git.kernel.org/stable/c/f90fff1e152dedf52b932240ebbd670d83330eca
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-38352
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38352.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38352
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
- https://github.com/farazsth98/chronomaly
