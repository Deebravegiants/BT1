# [C] ibmvnic: fix race between xmit and reset

## Summary
Severity: Critical
Advisory: CVE-2022-49201
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49201
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ibmvnic: fix race between xmit and reset

There is a race between reset and the transmit paths that can lead to
ibmvnic_xmit() accessing an scrq after it has been freed in the reset
path. It can result in a crash like:

	Kernel attempted to read user page (0) - exploit attempt? (uid: 0)
	BUG: Kernel NULL pointer dereference on read at 0x00000000
	Faulting instruction address: 0xc0080000016189f8
	Oops: Kernel access of bad area, sig: 11 [#1]
	...
	NIP [c0080000016189f8] ibmvnic_xmit+0x60/0xb60 [ibmvnic]
	LR [c000000000c0046c] dev_hard_start_xmit+0x11c/0x280
	Call Trace:
	[c008000001618f08] ibmvnic_xmit+0x570/0xb60 [ibmvnic] (unreliable)
	[c000000000c0046c] dev_hard_start_xmit+0x11c/0x280
	[c000000000c9cfcc] sch_direct_xmit+0xec/0x330
	[c000000000bfe640] __dev_xmit_skb+0x3a0/0x9d0
	[c000000000c00ad4] __dev_queue_xmit+0x394/0x730
	[c008000002db813c] __bond_start_xmit+0x254/0x450 [bonding]
	[c008000002db8378] bond_start_xmit+0x40/0xc0 [bonding]
	[c000000000c0046c] dev_hard_start_xmit+0x11c/0x280
	[c000000000c00ca4] __dev_queue_xmit+0x564/0x730
	[c000000000cf97e0] neigh_hh_output+0xd0/0x180
	[c000000000cfa69c] ip_finish_output2+0x31c/0x5c0
	[c000000000cfd244] __ip_queue_xmit+0x194/0x4f0
	[c000000000d2a3c4] __tcp_transmit_skb+0x434/0x9b0
	[c000000000d2d1e0] __tcp_retransmit_skb+0x1d0/0x6a0
	[c000000000d2d984] tcp_retransmit_skb+0x34/0x130
	[c000000000d310e8] tcp_retransmit_timer+0x388/0x6d0
	[c000000000d315ec] tcp_write_timer_handler+0x1bc/0x330
	[c000000000d317bc] tcp_write_timer+0x5c/0x200
	[c000000000243270] call_timer_fn+0x50/0x1c0
	[c000000000243704] __run_timers.part.0+0x324/0x460
	[c000000000243894] run_timer_softirq+0x54/0xa0
	[c000000000ea713c] __do_softirq+0x15c/0x3e0
	[c000000000166258] __irq_exit_rcu+0x158/0x190
	[c000000000166420] irq_exit+0x20/0x40
	[c00000000002853c] timer_interrupt+0x14c/0x2b0
	[c000000000009a00] decrementer_common_virt+0x210/0x220
	--- interrupt: 900 at plpar_hcall_norets_notrace+0x18/0x2c

The immediate cause of the crash is the access of tx_scrq in the following
snippet during a reset, where the tx_scrq can be either NULL or an address
that will soon be invalid:

	ibmvnic_xmit()
	{
		...
		tx_scrq = adapter->tx_scrq[queue_num];
		txq = netdev_get_tx_queue(netdev, queue_num);
		ind_bufp = &tx_scrq->ind_buf;

		if (test_bit(0, &adapter->resetting)) {
		...
	}

But beyond that, the call to ibmvnic_xmit() itself is not safe during a
reset and the reset path attempts to avoid this by stopping the queue in
ibmvnic_cleanup(). However just after the queue was stopped, an in-flight
ibmvnic_complete_tx() could have restarted the queue even as the reset is
progressing.

Since the queue was restarted we could get a call to ibmvnic_xmit() which
can then access the bad tx_scrq (or other fields).

We cannot however simply have ibmvnic_complete_tx() check the ->resetting
bit and skip starting the queue. This can race at the "back-end" of a good
reset which just restarted the queue but has not cleared the ->resetting
bit yet. If we skip restarting the queue due to ->resetting being true,
the queue would remain stopped indefinitely potentially leading to transmit
timeouts.

IOW ->resetting is too broad for this purpose. Instead use a new flag
that indicates whether or not the queues are active. Only the open/
reset paths control when the queues are active. ibmvnic_complete_tx()
and others wake up the queue only if the queue is marked active.

So we will have:
	A. reset/open thread in ibmvnic_cleanup() and __ibmvnic_open()

		->resetting = true
		->tx_queues_active = false
		disable tx queues
		...
		->tx_queues_active = true
		start tx queues

	B. Tx interrupt in ibmvnic_complete_tx():

		if (->tx_queues_active)
			netif_wake_subqueue();

To ensure that ->tx_queues_active and state of the queues are consistent,
we need a lock which:

	- must also be taken in the interrupt path (ibmvnic_complete_tx())
	- shared across the multiple
---truncated---

## References
- https://git.kernel.org/stable/c/1bd58abf595b6cf1ba6dd47ec887c4c009155fc9
- https://git.kernel.org/stable/c/4219196d1f662cb10a462eb9e076633a3fc31a15
- https://git.kernel.org/stable/c/475f9cce98b63bc145b4efa66fa51175d4cb345f
- https://git.kernel.org/stable/c/8507c6ade73cdbbbda5c3d31d67f52f2e1cf03fe
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49201.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49201
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
