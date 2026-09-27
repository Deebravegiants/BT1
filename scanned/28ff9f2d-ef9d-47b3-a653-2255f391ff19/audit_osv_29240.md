# [H] net: ks8851: Fix deadlock with the SPI chip variant

## Summary
Severity: High
Advisory: CVE-2024-41036
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41036
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.100, >=6.2.0 <6.6.41, >=6.7.0 <6.9.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ks8851: Fix deadlock with the SPI chip variant

When SMP is enabled and spinlocks are actually functional then there is
a deadlock with the 'statelock' spinlock between ks8851_start_xmit_spi
and ks8851_irq:

    watchdog: BUG: soft lockup - CPU#0 stuck for 27s!
    call trace:
      queued_spin_lock_slowpath+0x100/0x284
      do_raw_spin_lock+0x34/0x44
      ks8851_start_xmit_spi+0x30/0xb8
      ks8851_start_xmit+0x14/0x20
      netdev_start_xmit+0x40/0x6c
      dev_hard_start_xmit+0x6c/0xbc
      sch_direct_xmit+0xa4/0x22c
      __qdisc_run+0x138/0x3fc
      qdisc_run+0x24/0x3c
      net_tx_action+0xf8/0x130
      handle_softirqs+0x1ac/0x1f0
      __do_softirq+0x14/0x20
      ____do_softirq+0x10/0x1c
      call_on_irq_stack+0x3c/0x58
      do_softirq_own_stack+0x1c/0x28
      __irq_exit_rcu+0x54/0x9c
      irq_exit_rcu+0x10/0x1c
      el1_interrupt+0x38/0x50
      el1h_64_irq_handler+0x18/0x24
      el1h_64_irq+0x64/0x68
      __netif_schedule+0x6c/0x80
      netif_tx_wake_queue+0x38/0x48
      ks8851_irq+0xb8/0x2c8
      irq_thread_fn+0x2c/0x74
      irq_thread+0x10c/0x1b0
      kthread+0xc8/0xd8
      ret_from_fork+0x10/0x20

This issue has not been identified earlier because tests were done on
a device with SMP disabled and so spinlocks were actually NOPs.

Now use spin_(un)lock_bh for TX queue related locking to avoid execution
of softirq work synchronously that would lead to a deadlock.

## References
- https://git.kernel.org/stable/c/0913ec336a6c0c4a2b296bd9f74f8e41c4c83c8c
- https://git.kernel.org/stable/c/10fec0cd0e8f56ff06c46bb24254c7d8f8f2bbf0
- https://git.kernel.org/stable/c/80ece00137300d74642f2038c8fe5440deaf9f05
- https://git.kernel.org/stable/c/a0c69c492f4a8fad52f0a97565241c926160c9a4
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41036.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41036
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
