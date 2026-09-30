# [H] xsk: avoid data corruption on cq descriptor number

## Summary
Severity: High
Advisory: CVE-2025-40290
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2025-40290
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.17.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

xsk: avoid data corruption on cq descriptor number

Since commit 30f241fcf52a ("xsk: Fix immature cq descriptor
production"), the descriptor number is stored in skb control block and
xsk_cq_submit_addr_locked() relies on it to put the umem addrs onto
pool's completion queue.

skb control block shouldn't be used for this purpose as after transmit
xsk doesn't have control over it and other subsystems could use it. This
leads to the following kernel panic due to a NULL pointer dereference.

 BUG: kernel NULL pointer dereference, address: 0000000000000000
 #PF: supervisor read access in kernel mode
 #PF: error_code(0x0000) - not-present page
 PGD 0 P4D 0
 Oops: Oops: 0000 [#1] SMP NOPTI
 CPU: 2 UID: 1 PID: 927 Comm: p4xsk.bin Not tainted 6.16.12+deb14-cloud-amd64 #1 PREEMPT(lazy)  Debian 6.16.12-1
 Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.17.0-debian-1.17.0-1 04/01/2014
 RIP: 0010:xsk_destruct_skb+0xd0/0x180
 [...]
 Call Trace:
  <IRQ>
  ? napi_complete_done+0x7a/0x1a0
  ip_rcv_core+0x1bb/0x340
  ip_rcv+0x30/0x1f0
  __netif_receive_skb_one_core+0x85/0xa0
  process_backlog+0x87/0x130
  __napi_poll+0x28/0x180
  net_rx_action+0x339/0x420
  handle_softirqs+0xdc/0x320
  ? handle_edge_irq+0x90/0x1e0
  do_softirq.part.0+0x3b/0x60
  </IRQ>
  <TASK>
  __local_bh_enable_ip+0x60/0x70
  __dev_direct_xmit+0x14e/0x1f0
  __xsk_generic_xmit+0x482/0xb70
  ? __remove_hrtimer+0x41/0xa0
  ? __xsk_generic_xmit+0x51/0xb70
  ? _raw_spin_unlock_irqrestore+0xe/0x40
  xsk_sendmsg+0xda/0x1c0
  __sys_sendto+0x1ee/0x200
  __x64_sys_sendto+0x24/0x30
  do_syscall_64+0x84/0x2f0
  ? __pfx_pollwake+0x10/0x10
  ? __rseq_handle_notify_resume+0xad/0x4c0
  ? restore_fpregs_from_fpstate+0x3c/0x90
  ? switch_fpu_return+0x5b/0xe0
  ? do_syscall_64+0x204/0x2f0
  ? do_syscall_64+0x204/0x2f0
  ? do_syscall_64+0x204/0x2f0
  entry_SYSCALL_64_after_hwframe+0x76/0x7e
  </TASK>
 [...]
 Kernel panic - not syncing: Fatal exception in interrupt
 Kernel Offset: 0x1c000000 from 0xffffffff81000000 (relocation range: 0xffffffff80000000-0xffffffffbfffffff)

Instead use the skb destructor_arg pointer along with pointer tagging.
As pointers are always aligned to 8B, use the bottom bit to indicate
whether this a single address or an allocated struct containing several
addresses.

## References
- https://bugs.debian.org/1118437
- https://git.kernel.org/stable/c/0ebc27a4c67d44e5ce88d21cdad8201862b78837
- https://git.kernel.org/stable/c/c5ea2e50b5c9aa80c5b53526257540f0c26cd66d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40290.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40290
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
