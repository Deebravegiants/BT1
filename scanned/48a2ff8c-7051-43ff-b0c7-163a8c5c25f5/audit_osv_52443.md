# [M] CVE-2021-47454

## Summary
Severity: Medium
Advisory: CVE-2021-47454
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47454
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

powerpc/smp: do not decrement idle task preempt count in CPU offline

With PREEMPT_COUNT=y, when a CPU is offlined and then onlined again, we
get:

BUG: scheduling while atomic: swapper/1/0/0x00000000
no locks held by swapper/1/0.
CPU: 1 PID: 0 Comm: swapper/1 Not tainted 5.15.0-rc2+ #100
Call Trace:
 dump_stack_lvl+0xac/0x108
 __schedule_bug+0xac/0xe0
 __schedule+0xcf8/0x10d0
 schedule_idle+0x3c/0x70
 do_idle+0x2d8/0x4a0
 cpu_startup_entry+0x38/0x40
 start_secondary+0x2ec/0x3a0
 start_secondary_prolog+0x10/0x14

This is because powerpc's arch_cpu_idle_dead() decrements the idle task's
preempt count, for reasons explained in commit a7c2bb8279d2 ("powerpc:
Re-enable preemption before cpu_die()"), specifically "start_secondary()
expects a preempt_count() of 0."

However, since commit 2c669ef6979c ("powerpc/preempt: Don't touch the idle
task's preempt_count during hotplug") and commit f1a0a376ca0c ("sched/core:
Initialize the idle task with preemption disabled"), that justification no
longer holds.

The idle task isn't supposed to re-enable preemption, so remove the
vestigial preempt_enable() from the CPU offline path.

Tested with pseries and powernv in qemu, and pseries on PowerVM.

## References
- https://git.kernel.org/stable/c/3ea0b497a7a2fff6a4b7090310c9f52c91975934
- https://git.kernel.org/stable/c/53770a411559cf7bc0906d1df319cc533d2f4f58
- https://git.kernel.org/stable/c/787252a10d9422f3058df9a4821f389e5326c440
