# [H] net: ks8851: Handle softirqs at the end of IRQ thread to fix hang

## Summary
Severity: High
Advisory: CVE-2024-35971
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-20
Source: https://osv.dev/vulnerability/CVE-2024-35971
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <6.1.87, >=6.2.0 <6.6.28, >=6.7.0 <6.8.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ks8851: Handle softirqs at the end of IRQ thread to fix hang

The ks8851_irq() thread may call ks8851_rx_pkts() in case there are
any packets in the MAC FIFO, which calls netif_rx(). This netif_rx()
implementation is guarded by local_bh_disable() and local_bh_enable().
The local_bh_enable() may call do_softirq() to run softirqs in case
any are pending. One of the softirqs is net_rx_action, which ultimately
reaches the driver .start_xmit callback. If that happens, the system
hangs. The entire call chain is below:

ks8851_start_xmit_par from netdev_start_xmit
netdev_start_xmit from dev_hard_start_xmit
dev_hard_start_xmit from sch_direct_xmit
sch_direct_xmit from __dev_queue_xmit
__dev_queue_xmit from __neigh_update
__neigh_update from neigh_update
neigh_update from arp_process.constprop.0
arp_process.constprop.0 from __netif_receive_skb_one_core
__netif_receive_skb_one_core from process_backlog
process_backlog from __napi_poll.constprop.0
__napi_poll.constprop.0 from net_rx_action
net_rx_action from __do_softirq
__do_softirq from call_with_stack
call_with_stack from do_softirq
do_softirq from __local_bh_enable_ip
__local_bh_enable_ip from netif_rx
netif_rx from ks8851_irq
ks8851_irq from irq_thread_fn
irq_thread_fn from irq_thread
irq_thread from kthread
kthread from ret_from_fork

The hang happens because ks8851_irq() first locks a spinlock in
ks8851_par.c ks8851_lock_par() spin_lock_irqsave(&ksp->lock, ...)
and with that spinlock locked, calls netif_rx(). Once the execution
reaches ks8851_start_xmit_par(), it calls ks8851_lock_par() again
which attempts to claim the already locked spinlock again, and the
hang happens.

Move the do_softirq() call outside of the spinlock protected section
of ks8851_irq() by disabling BHs around the entire spinlock protected
section of ks8851_irq() handler. Place local_bh_enable() outside of
the spinlock protected section, so that it can trigger do_softirq()
without the ks8851_par.c ks8851_lock_par() spinlock being held, and
safely call ks8851_start_xmit_par() without attempting to lock the
already locked spinlock.

Since ks8851_irq() is protected by local_bh_disable()/local_bh_enable()
now, replace netif_rx() with __netif_rx() which is not duplicating the
local_bh_disable()/local_bh_enable() calls.

## References
- http://www.openwall.com/lists/oss-security/2024/05/30/1
- http://www.openwall.com/lists/oss-security/2024/05/30/2
- https://git.kernel.org/stable/c/492337a4fbd1421b42df684ee9b34be2a2722540
- https://git.kernel.org/stable/c/49d5d70538b6b8f2a3f8f1ac30c1f921d4a0929b
- https://git.kernel.org/stable/c/be0384bf599cf1eb8d337517feeb732d71f75a6f
- https://git.kernel.org/stable/c/cba376eb036c2c20077b41d47b317d8218fe754f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35971.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35971
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
