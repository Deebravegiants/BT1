# [H] smc91x: fix broken irq-context in PREEMPT_RT

## Summary
Severity: High
Advisory: CVE-2025-71132
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-14
Source: https://osv.dev/vulnerability/CVE-2025-71132
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.198, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.64, >=6.13.0 <6.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

smc91x: fix broken irq-context in PREEMPT_RT

When smc91x.c is built with PREEMPT_RT, the following splat occurs
in FVP_RevC:

[   13.055000] smc91x LNRO0003:00 eth0: link up, 10Mbps, half-duplex, lpa 0x0000
[   13.062137] BUG: workqueue leaked atomic, lock or RCU: kworker/2:1[106]
[   13.062137]      preempt=0x00000000 lock=0->0 RCU=0->1 workfn=mld_ifc_work
[   13.062266] C
** replaying previous printk message **
[   13.062266] CPU: 2 UID: 0 PID: 106 Comm: kworker/2:1 Not tainted 6.18.0-dirty #179 PREEMPT_{RT,(full)}
[   13.062353] Hardware name:  , BIOS
[   13.062382] Workqueue: mld mld_ifc_work
[   13.062469] Call trace:
[   13.062494]  show_stack+0x24/0x40 (C)
[   13.062602]  __dump_stack+0x28/0x48
[   13.062710]  dump_stack_lvl+0x7c/0xb0
[   13.062818]  dump_stack+0x18/0x34
[   13.062926]  process_scheduled_works+0x294/0x450
[   13.063043]  worker_thread+0x260/0x3d8
[   13.063124]  kthread+0x1c4/0x228
[   13.063235]  ret_from_fork+0x10/0x20

This happens because smc_special_trylock() disables IRQs even on PREEMPT_RT,
but smc_special_unlock() does not restore IRQs on PREEMPT_RT.
The reason is that smc_special_unlock() calls spin_unlock_irqrestore(),
and rcu_read_unlock_bh() in __dev_queue_xmit() cannot invoke
rcu_read_unlock() through __local_bh_enable_ip() when current->softirq_disable_cnt becomes zero.

To address this issue, replace smc_special_trylock() with spin_trylock_irqsave().

## References
- https://git.kernel.org/stable/c/1c4cb705e733250d13243f6a69b8b5a92e39b9f6
- https://git.kernel.org/stable/c/36561b86cb2501647662cfaf91286dd6973804a6
- https://git.kernel.org/stable/c/6402078bd9d1ed46e79465e1faaa42e3458f8a33
- https://git.kernel.org/stable/c/9d222141b00156509d67d80c771fbefa92c43ace
- https://git.kernel.org/stable/c/b6018d5c1a8f09d5efe4d6961d7ee45fdf3a7ce3
- https://git.kernel.org/stable/c/ef277ae121b3249c99994652210a326b52d527b0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71132.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71132
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
