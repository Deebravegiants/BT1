# [M] riscv: Fix sleeping in invalid context in die()

## Summary
Severity: Medium
Advisory: CVE-2024-57939
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-21
Source: https://osv.dev/vulnerability/CVE-2024-57939
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.10.234, >=5.11.0 <5.15.177, >=5.16.0 <6.1.125, >=6.2.0 <6.6.72, >=6.7.0 <6.12.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

riscv: Fix sleeping in invalid context in die()

die() can be called in exception handler, and therefore cannot sleep.
However, die() takes spinlock_t which can sleep with PREEMPT_RT enabled.
That causes the following warning:

BUG: sleeping function called from invalid context at kernel/locking/spinlock_rt.c:48
in_atomic(): 1, irqs_disabled(): 1, non_block: 0, pid: 285, name: mutex
preempt_count: 110001, expected: 0
RCU nest depth: 0, expected: 0
CPU: 0 UID: 0 PID: 285 Comm: mutex Not tainted 6.12.0-rc7-00022-ge19049cf7d56-dirty #234
Hardware name: riscv-virtio,qemu (DT)
Call Trace:
    dump_backtrace+0x1c/0x24
    show_stack+0x2c/0x38
    dump_stack_lvl+0x5a/0x72
    dump_stack+0x14/0x1c
    __might_resched+0x130/0x13a
    rt_spin_lock+0x2a/0x5c
    die+0x24/0x112
    do_trap_insn_illegal+0xa0/0xea
    _new_vmalloc_restore_context_a0+0xcc/0xd8
Oops - illegal instruction [#1]

Switch to use raw_spinlock_t, which does not sleep even with PREEMPT_RT
enabled.

## References
- https://git.kernel.org/stable/c/10c24df2e303f517fab0359392c11b6b1d553f2b
- https://git.kernel.org/stable/c/6a97f4118ac07cfdc316433f385dbdc12af5025e
- https://git.kernel.org/stable/c/76ab0afcdbe8c9685b589016ee1c0e25fe596707
- https://git.kernel.org/stable/c/8c38baa03ac8e18140faf36a3b955d30cad48e74
- https://git.kernel.org/stable/c/c21df31fc2a4afc02a6e56511364e9e793ea92ec
- https://git.kernel.org/stable/c/f48f060a4b36b5e96628f6c3fb1540f1e8dedb69
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57939.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57939
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
