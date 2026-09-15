# [H] net: ks8851: Queue RX packets in IRQ handler instead of disabling BHs

## Summary
Severity: High
Advisory: CVE-2024-36962
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-03
Source: https://osv.dev/vulnerability/CVE-2024-36962
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.87 <6.1.91, >=6.6.28 <6.6.31, >=6.8.7 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ks8851: Queue RX packets in IRQ handler instead of disabling BHs

Currently the driver uses local_bh_disable()/local_bh_enable() in its
IRQ handler to avoid triggering net_rx_action() softirq on exit from
netif_rx(). The net_rx_action() could trigger this driver .start_xmit
callback, which is protected by the same lock as the IRQ handler, so
calling the .start_xmit from netif_rx() from the IRQ handler critical
section protected by the lock could lead to an attempt to claim the
already claimed lock, and a hang.

The local_bh_disable()/local_bh_enable() approach works only in case
the IRQ handler is protected by a spinlock, but does not work if the
IRQ handler is protected by mutex, i.e. this works for KS8851 with
Parallel bus interface, but not for KS8851 with SPI bus interface.

Remove the BH manipulation and instead of calling netif_rx() inside
the IRQ handler code protected by the lock, queue all the received
SKBs in the IRQ handler into a queue first, and once the IRQ handler
exits the critical section protected by the lock, dequeue all the
queued SKBs and push them all into netif_rx(). At this point, it is
safe to trigger the net_rx_action() softirq, since the netif_rx()
call is outside of the lock that protects the IRQ handler.

## References
- https://git.kernel.org/stable/c/7e2901a2a9195da76111f351584bf77552a038f0
- https://git.kernel.org/stable/c/8a3ff43dcbab7c96f9e8cf2bd1049ab8d6e59545
- https://git.kernel.org/stable/c/ae87f661f3c1a3134a7ed86ab69bf9f12af88993
- https://git.kernel.org/stable/c/e0863634bf9f7cf36291ebb5bfa2d16632f79c49
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36962.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36962
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
