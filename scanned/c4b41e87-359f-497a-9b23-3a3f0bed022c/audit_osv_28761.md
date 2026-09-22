# [H] netfilter: nfnetlink_queue: acquire rcu_read_lock() in instance_destroy_rcu()

## Summary
Severity: High
Advisory: CVE-2024-36286
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-21
Source: https://osv.dev/vulnerability/CVE-2024-36286
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.25 <4.19.316, >=4.20.0 <5.4.278, >=5.5.0 <5.10.219, >=5.11.0 <5.15.161, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.9.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nfnetlink_queue: acquire rcu_read_lock() in instance_destroy_rcu()

syzbot reported that nf_reinject() could be called without rcu_read_lock() :

WARNING: suspicious RCU usage
6.9.0-rc7-syzkaller-02060-g5c1672705a1a #0 Not tainted

net/netfilter/nfnetlink_queue.c:263 suspicious rcu_dereference_check() usage!

other info that might help us debug this:

rcu_scheduler_active = 2, debug_locks = 1
2 locks held by syz-executor.4/13427:
  #0: ffffffff8e334f60 (rcu_callback){....}-{0:0}, at: rcu_lock_acquire include/linux/rcupdate.h:329 [inline]
  #0: ffffffff8e334f60 (rcu_callback){....}-{0:0}, at: rcu_do_batch kernel/rcu/tree.c:2190 [inline]
  #0: ffffffff8e334f60 (rcu_callback){....}-{0:0}, at: rcu_core+0xa86/0x1830 kernel/rcu/tree.c:2471
  #1: ffff88801ca92958 (&inst->lock){+.-.}-{2:2}, at: spin_lock_bh include/linux/spinlock.h:356 [inline]
  #1: ffff88801ca92958 (&inst->lock){+.-.}-{2:2}, at: nfqnl_flush net/netfilter/nfnetlink_queue.c:405 [inline]
  #1: ffff88801ca92958 (&inst->lock){+.-.}-{2:2}, at: instance_destroy_rcu+0x30/0x220 net/netfilter/nfnetlink_queue.c:172

stack backtrace:
CPU: 0 PID: 13427 Comm: syz-executor.4 Not tainted 6.9.0-rc7-syzkaller-02060-g5c1672705a1a #0
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 04/02/2024
Call Trace:
 <IRQ>
  __dump_stack lib/dump_stack.c:88 [inline]
  dump_stack_lvl+0x241/0x360 lib/dump_stack.c:114
  lockdep_rcu_suspicious+0x221/0x340 kernel/locking/lockdep.c:6712
  nf_reinject net/netfilter/nfnetlink_queue.c:323 [inline]
  nfqnl_reinject+0x6ec/0x1120 net/netfilter/nfnetlink_queue.c:397
  nfqnl_flush net/netfilter/nfnetlink_queue.c:410 [inline]
  instance_destroy_rcu+0x1ae/0x220 net/netfilter/nfnetlink_queue.c:172
  rcu_do_batch kernel/rcu/tree.c:2196 [inline]
  rcu_core+0xafd/0x1830 kernel/rcu/tree.c:2471
  handle_softirqs+0x2d6/0x990 kernel/softirq.c:554
  __do_softirq kernel/softirq.c:588 [inline]
  invoke_softirq kernel/softirq.c:428 [inline]
  __irq_exit_rcu+0xf4/0x1c0 kernel/softirq.c:637
  irq_exit_rcu+0x9/0x30 kernel/softirq.c:649
  instr_sysvec_apic_timer_interrupt arch/x86/kernel/apic/apic.c:1043 [inline]
  sysvec_apic_timer_interrupt+0xa6/0xc0 arch/x86/kernel/apic/apic.c:1043
 </IRQ>
 <TASK>

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-398330.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://git.kernel.org/stable/c/215df6490e208bfdd5b3012f5075e7f8736f3e7a
- https://git.kernel.org/stable/c/25ea5377e3d2921a0f96ae2551f5ab1b36825dd4
- https://git.kernel.org/stable/c/3989b817857f4890fab9379221a9d3f52bf5c256
- https://git.kernel.org/stable/c/68f40354a3851df46c27be96b84f11ae193e36c5
- https://git.kernel.org/stable/c/8658bd777cbfcb0c13df23d0ea120e70517761b9
- https://git.kernel.org/stable/c/8f365564af898819a523f1a8cf5c6ce053e9f718
- https://git.kernel.org/stable/c/dc21c6cc3d6986d938efbf95de62473982c98dec
- https://git.kernel.org/stable/c/e01065b339e323b3dfa1be217fd89e9b3208b0ab
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36286.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36286
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
