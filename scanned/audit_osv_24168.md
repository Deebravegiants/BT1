# [M] led: qcom-lpg: Fix sleeping in atomic

## Summary
Severity: Medium
Advisory: CVE-2022-50371
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2022-50371
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

led: qcom-lpg: Fix sleeping in atomic

lpg_brighness_set() function can sleep, while led's brightness_set()
callback must be non-blocking. Change LPG driver to use
brightness_set_blocking() instead.

BUG: sleeping function called from invalid context at kernel/locking/mutex.c:580
in_atomic(): 1, irqs_disabled(): 0, non_block: 0, pid: 0, name: swapper/0
preempt_count: 101, expected: 0
INFO: lockdep is turned off.
CPU: 0 PID: 0 Comm: swapper/0 Tainted: G        W          6.1.0-rc1-00014-gbe99b089c6fc-dirty #85
Hardware name: Qualcomm Technologies, Inc. DB820c (DT)
Call trace:
 dump_backtrace.part.0+0xe4/0xf0
 show_stack+0x18/0x40
 dump_stack_lvl+0x88/0xb4
 dump_stack+0x18/0x34
 __might_resched+0x170/0x254
 __might_sleep+0x48/0x9c
 __mutex_lock+0x4c/0x400
 mutex_lock_nested+0x2c/0x40
 lpg_brightness_single_set+0x40/0x90
 led_set_brightness_nosleep+0x34/0x60
 led_heartbeat_function+0x80/0x170
 call_timer_fn+0xb8/0x340
 __run_timers.part.0+0x20c/0x254
 run_timer_softirq+0x3c/0x7c
 _stext+0x14c/0x578
 ____do_softirq+0x10/0x20
 call_on_irq_stack+0x2c/0x5c
 do_softirq_own_stack+0x1c/0x30
 __irq_exit_rcu+0x164/0x170
 irq_exit_rcu+0x10/0x40
 el1_interrupt+0x38/0x50
 el1h_64_irq_handler+0x18/0x2c
 el1h_64_irq+0x64/0x68
 cpuidle_enter_state+0xc8/0x380
 cpuidle_enter+0x38/0x50
 do_idle+0x244/0x2d0
 cpu_startup_entry+0x24/0x30
 rest_init+0x128/0x1a0
 arch_post_acpi_subsys_init+0x0/0x18
 start_kernel+0x6f4/0x734
 __primary_switched+0xbc/0xc4

## References
- https://git.kernel.org/stable/c/3031993b3474794ecb71b6f969a3e60e4bda9d8a
- https://git.kernel.org/stable/c/380304391fa7fb084745f26b4b9a59f4666520c1
- https://git.kernel.org/stable/c/9deba7b51d5ee7a2d93fabb69f9b8189241f90e3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50371.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50371
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
