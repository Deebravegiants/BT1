# [H] net: ks8851: Reinstate disabling of BHs around IRQ handler

## Summary
Severity: High
Advisory: CVE-2026-46031
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46031
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.86, >=6.9.0 <6.18.27, >=6.13.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ks8851: Reinstate disabling of BHs around IRQ handler

If the driver executes ks8851_irq() AND a TX packet has been sent, then
the driver enables TX queue via netif_wake_queue() which schedules TX
softirq to queue packets for this device.

If CONFIG_PREEMPT_RT=y is set AND a packet has also been received by
the MAC, then ks8851_rx_pkts() calls netdev_alloc_skb_ip_align() to
allocate SKBs for the received packets. If netdev_alloc_skb_ip_align()
is called with BH enabled, then local_bh_enable() at the end of
netdev_alloc_skb_ip_align() will trigger the pending softirq processing,
which may ultimately call the .xmit callback ks8851_start_xmit_par().
The ks8851_start_xmit_par() will try to lock struct ks8851_net_par
.lock spinlock, which is already locked by ks8851_irq() from which
ks8851_start_xmit_par() was called. This leads to a deadlock, which
is reported by the kernel, including a trace listed below.

If CONFIG_PREEMPT_RT is not set, then since commit 0913ec336a6c0
("net: ks8851: Fix deadlock with the SPI chip variant") the deadlock
can also be triggered without received packet in the RX FIFO. The
pending softirqs will be processed on return from
spin_unlock_bh(&ks->statelock) in ks8851_irq(), which triggers the
deadlock as well.

Fix the problem by disabling BH around critical sections, including the
IRQ handler, thus preventing the net_tx_action() softirq from triggering
during these critical sections. The net_tx_action() softirq is triggered
once BH are re-enabled and at the end of the IRQ handler, once all the
other IRQ handler actions have been completed.

 __schedule from schedule_rtlock+0x1c/0x34
 schedule_rtlock from rtlock_slowlock_locked+0x548/0x904
 rtlock_slowlock_locked from rt_spin_lock+0x60/0x9c
 rt_spin_lock from ks8851_start_xmit_par+0x74/0x1a8
 ks8851_start_xmit_par from netdev_start_xmit+0x20/0x44
 netdev_start_xmit from dev_hard_start_xmit+0xd0/0x188
 dev_hard_start_xmit from sch_direct_xmit+0xb8/0x25c
 sch_direct_xmit from __qdisc_run+0x1f8/0x4ec
 __qdisc_run from qdisc_run+0x1c/0x28
 qdisc_run from net_tx_action+0x1f0/0x268
 net_tx_action from handle_softirqs+0x1a4/0x270
 handle_softirqs from __local_bh_enable_ip+0xcc/0xe0
 __local_bh_enable_ip from __alloc_skb+0xd8/0x128
 __alloc_skb from __netdev_alloc_skb+0x3c/0x19c
 __netdev_alloc_skb from ks8851_irq+0x388/0x4d4
 ks8851_irq from irq_thread_fn+0x24/0x64
 irq_thread_fn from irq_thread+0x178/0x28c
 irq_thread from kthread+0x12c/0x138
 kthread from ret_from_fork+0x14/0x28

## References
- https://git.kernel.org/stable/c/1962027a6d223f90df8b372929f9d1a8d321ad6a
- https://git.kernel.org/stable/c/21f1707a8e978558dcb11b053855521e32ac0eec
- https://git.kernel.org/stable/c/518040324067d8efaa2da1992297b7e7bf5640f4
- https://git.kernel.org/stable/c/5c9fcac3c872224316714d0d8914d9af16c76a6d
- https://git.kernel.org/stable/c/640a7631d31db87d5fa1b34cea44a99b6e78854b
- https://git.kernel.org/stable/c/be8aad558b4675f45b43080f81a9ffdeddea73a5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46031.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46031
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
