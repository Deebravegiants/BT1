# [H] lan966x: Fix sleeping in atomic context

## Summary
Severity: High
Advisory: CVE-2025-68320
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68320
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.6.117, >=6.7.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

lan966x: Fix sleeping in atomic context

The following warning was seen when we try to connect using ssh to the device.

BUG: sleeping function called from invalid context at kernel/locking/mutex.c:575
in_atomic(): 1, irqs_disabled(): 0, non_block: 0, pid: 104, name: dropbear
preempt_count: 1, expected: 0
INFO: lockdep is turned off.
CPU: 0 UID: 0 PID: 104 Comm: dropbear Tainted: G        W           6.18.0-rc2-00399-g6f1ab1b109b9-dirty #530 NONE
Tainted: [W]=WARN
Hardware name: Generic DT based system
Call trace:
 unwind_backtrace from show_stack+0x10/0x14
 show_stack from dump_stack_lvl+0x7c/0xac
 dump_stack_lvl from __might_resched+0x16c/0x2b0
 __might_resched from __mutex_lock+0x64/0xd34
 __mutex_lock from mutex_lock_nested+0x1c/0x24
 mutex_lock_nested from lan966x_stats_get+0x5c/0x558
 lan966x_stats_get from dev_get_stats+0x40/0x43c
 dev_get_stats from dev_seq_printf_stats+0x3c/0x184
 dev_seq_printf_stats from dev_seq_show+0x10/0x30
 dev_seq_show from seq_read_iter+0x350/0x4ec
 seq_read_iter from seq_read+0xfc/0x194
 seq_read from proc_reg_read+0xac/0x100
 proc_reg_read from vfs_read+0xb0/0x2b0
 vfs_read from ksys_read+0x6c/0xec
 ksys_read from ret_fast_syscall+0x0/0x1c
Exception stack(0xf0b11fa8 to 0xf0b11ff0)
1fa0:                   00000001 00001000 00000008 be9048d8 00001000 00000001
1fc0: 00000001 00001000 00000008 00000003 be905920 0000001e 00000000 00000001
1fe0: 0005404c be9048c0 00018684 b6ec2cd8

It seems that we are using a mutex in a atomic context which is wrong.
Change the mutex with a spinlock.

## References
- https://git.kernel.org/stable/c/0216721ce71252f60d89af49c8dff613358058d3
- https://git.kernel.org/stable/c/3ac743c60ec502163c435712d527eeced8d83348
- https://git.kernel.org/stable/c/5a5d2f7727752b64d13263eacd9f8d08a322e662
- https://git.kernel.org/stable/c/c8ab03aa5bd9fd8bfe5d9552d8605826759fdd4d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68320.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68320
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
