# [H] net: defer final 'struct net' free in netns dismantle

## Summary
Severity: High
Advisory: CVE-2024-56658
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56658
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <5.10.237, >=5.11.0 <5.15.181, >=5.16.0 <6.1.121, >=6.2.0 <6.6.67, >=6.7.0 <6.12.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: defer final 'struct net' free in netns dismantle

Ilya reported a slab-use-after-free in dst_destroy [1]

Issue is in xfrm6_net_init() and xfrm4_net_init() :

They copy xfrm[46]_dst_ops_template into net->xfrm.xfrm[46]_dst_ops.

But net structure might be freed before all the dst callbacks are
called. So when dst_destroy() calls later :

if (dst->ops->destroy)
    dst->ops->destroy(dst);

dst->ops points to the old net->xfrm.xfrm[46]_dst_ops, which has been freed.

See a relevant issue fixed in :

ac888d58869b ("net: do not delay dst_entries_add() in dst_release()")

A fix is to queue the 'struct net' to be freed after one
another cleanup_net() round (and existing rcu_barrier())

[1]

BUG: KASAN: slab-use-after-free in dst_destroy (net/core/dst.c:112)
Read of size 8 at addr ffff8882137ccab0 by task swapper/37/0
Dec 03 05:46:18 kernel:
CPU: 37 UID: 0 PID: 0 Comm: swapper/37 Kdump: loaded Not tainted 6.12.0 #67
Hardware name: Red Hat KVM/RHEL, BIOS 1.16.1-1.el9 04/01/2014
Call Trace:
 <IRQ>
dump_stack_lvl (lib/dump_stack.c:124)
print_address_description.constprop.0 (mm/kasan/report.c:378)
? dst_destroy (net/core/dst.c:112)
print_report (mm/kasan/report.c:489)
? dst_destroy (net/core/dst.c:112)
? kasan_addr_to_slab (mm/kasan/common.c:37)
kasan_report (mm/kasan/report.c:603)
? dst_destroy (net/core/dst.c:112)
? rcu_do_batch (kernel/rcu/tree.c:2567)
dst_destroy (net/core/dst.c:112)
rcu_do_batch (kernel/rcu/tree.c:2567)
? __pfx_rcu_do_batch (kernel/rcu/tree.c:2491)
? lockdep_hardirqs_on_prepare (kernel/locking/lockdep.c:4339 kernel/locking/lockdep.c:4406)
rcu_core (kernel/rcu/tree.c:2825)
handle_softirqs (kernel/softirq.c:554)
__irq_exit_rcu (kernel/softirq.c:589 kernel/softirq.c:428 kernel/softirq.c:637)
irq_exit_rcu (kernel/softirq.c:651)
sysvec_apic_timer_interrupt (arch/x86/kernel/apic/apic.c:1049 arch/x86/kernel/apic/apic.c:1049)
 </IRQ>
 <TASK>
asm_sysvec_apic_timer_interrupt (./arch/x86/include/asm/idtentry.h:702)
RIP: 0010:default_idle (./arch/x86/include/asm/irqflags.h:37 ./arch/x86/include/asm/irqflags.h:92 arch/x86/kernel/process.c:743)
Code: 00 4d 29 c8 4c 01 c7 4c 29 c2 e9 6e ff ff ff 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 66 90 0f 00 2d c7 c9 27 00 fb f4 <fa> c3 cc cc cc cc 66 66 2e 0f 1f 84 00 00 00 00 00 0f 1f 40 00 90
RSP: 0018:ffff888100d2fe00 EFLAGS: 00000246
RAX: 00000000001870ed RBX: 1ffff110201a5fc2 RCX: ffffffffb61a3e46
RDX: 0000000000000000 RSI: 0000000000000000 RDI: ffffffffb3d4d123
RBP: 0000000000000000 R08: 0000000000000001 R09: ffffed11c7e1835d
R10: ffff888e3f0c1aeb R11: 0000000000000000 R12: 0000000000000000
R13: ffff888100d20000 R14: dffffc0000000000 R15: 0000000000000000
? ct_kernel_exit.constprop.0 (kernel/context_tracking.c:148)
? cpuidle_idle_call (kernel/sched/idle.c:186)
default_idle_call (./include/linux/cpuidle.h:143 kernel/sched/idle.c:118)
cpuidle_idle_call (kernel/sched/idle.c:186)
? __pfx_cpuidle_idle_call (kernel/sched/idle.c:168)
? lock_release (kernel/locking/lockdep.c:467 kernel/locking/lockdep.c:5848)
? lockdep_hardirqs_on_prepare (kernel/locking/lockdep.c:4347 kernel/locking/lockdep.c:4406)
? tsc_verify_tsc_adjust (arch/x86/kernel/tsc_sync.c:59)
do_idle (kernel/sched/idle.c:326)
cpu_startup_entry (kernel/sched/idle.c:423 (discriminator 1))
start_secondary (arch/x86/kernel/smpboot.c:202 arch/x86/kernel/smpboot.c:282)
? __pfx_start_secondary (arch/x86/kernel/smpboot.c:232)
? soft_restart_cpu (arch/x86/kernel/head_64.S:452)
common_startup_64 (arch/x86/kernel/head_64.S:414)
 </TASK>
Dec 03 05:46:18 kernel:
Allocated by task 12184:
kasan_save_stack (mm/kasan/common.c:48)
kasan_save_track (./arch/x86/include/asm/current.h:49 mm/kasan/common.c:60 mm/kasan/common.c:69)
__kasan_slab_alloc (mm/kasan/common.c:319 mm/kasan/common.c:345)
kmem_cache_alloc_noprof (mm/slub.c:4085 mm/slub.c:4134 mm/slub.c:4141)
copy_net_ns (net/core/net_namespace.c:421 net/core/net_namespace.c:480)
create_new_namespaces
---truncated---

## References
- https://git.kernel.org/stable/c/0f6ede9fbc747e2553612271bce108f7517e7a45
- https://git.kernel.org/stable/c/3267b254dc0a04dfa362a2be24573cfa6d2d78f5
- https://git.kernel.org/stable/c/6610c7f8a8d47fd1123eed55ba8c11c2444d8842
- https://git.kernel.org/stable/c/b7a79e51297f7b82adb687086f5cb2da446f1e40
- https://git.kernel.org/stable/c/c261dcd61c9e88a8f1a66654354d32295a975230
- https://git.kernel.org/stable/c/dac465986a4a38cd2f13e934f562b6ca344e5720
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56658.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56658
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
