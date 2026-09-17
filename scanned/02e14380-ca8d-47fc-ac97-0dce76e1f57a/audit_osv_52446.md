# [M] CVE-2021-47457

## Summary
Severity: Medium
Advisory: CVE-2021-47457
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47457
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: isotp: isotp_sendmsg(): add result check for wait_event_interruptible()

Using wait_event_interruptible() to wait for complete transmission,
but do not check the result of wait_event_interruptible() which can be
interrupted. It will result in TX buffer has multiple accessors and
the later process interferes with the previous process.

Following is one of the problems reported by syzbot.

=============================================================
WARNING: CPU: 0 PID: 0 at net/can/isotp.c:840 isotp_tx_timer_handler+0x2e0/0x4c0
CPU: 0 PID: 0 Comm: swapper/0 Not tainted 5.13.0-rc7+ #68
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.13.0-1ubuntu1 04/01/2014
RIP: 0010:isotp_tx_timer_handler+0x2e0/0x4c0
Call Trace:
 <IRQ>
 ? isotp_setsockopt+0x390/0x390
 __hrtimer_run_queues+0xb8/0x610
 hrtimer_run_softirq+0x91/0xd0
 ? rcu_read_lock_sched_held+0x4d/0x80
 __do_softirq+0xe8/0x553
 irq_exit_rcu+0xf8/0x100
 sysvec_apic_timer_interrupt+0x9e/0xc0
 </IRQ>
 asm_sysvec_apic_timer_interrupt+0x12/0x20

Add result check for wait_event_interruptible() in isotp_sendmsg()
to avoid multiple accessers for tx buffer.

## References
- https://git.kernel.org/stable/c/053bc12df0d6097c1126d0e14fa778a0a8faeb64
- https://git.kernel.org/stable/c/9acf636215a6ce9362fe618e7da4913b8bfe84c8
- https://git.kernel.org/stable/c/a76abedd2be3926d6deba236a935c7f98abf9110
