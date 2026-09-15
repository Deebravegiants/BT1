# [H] can: isotp: use unconditional synchronize_rcu() in isotp_release()

## Summary
Severity: High
Advisory: CVE-2026-72126
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72126
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.261, >=5.11.0 <5.15.212, >=5.14.0 <6.1.178, >=5.16.0 <6.6.145, >=6.2.0 <6.12.97, >=6.7.0 <6.18.40, >=6.13.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: isotp: use unconditional synchronize_rcu() in isotp_release()

isotp_notify() unregisters the (RCU) CAN filters via can_rx_unregister()
and clears so->bound without waiting for a grace period. isotp_release()
uses so->bound to decide whether it needs to call synchronize_rcu()
before cancelling so->rxtimer, so when NETDEV_UNREGISTER runs first it
skips that synchronize_rcu() and can cancel the timer while an
in-flight isotp_rcv() is still executing and about to re-arm it via
isotp_send_fc(), leading to a use-after-free timer callback on the
freed socket.

sakisho-bot remarked a problem with rtnl_lock held in isotp_notify(),
therefore make isotp_release() always call synchronize_rcu() before
cancelling the timers, regardless of so->bound. This still closes the
original race (isotp_notify() clearing so->bound without waiting for
in-flight isotp_rcv() callers before isotp_release() cancels the RX
timer) without adding any RCU wait to the netdevice notifier path.

## References
- https://git.kernel.org/stable/c/15413a082df69175c2f96aeab4c26fe1ff7cff03
- https://git.kernel.org/stable/c/59672aa4bcd8d32172c1ff6a179583981d6acabc
- https://git.kernel.org/stable/c/6280eda96e0707264849fa7d036fed873c1f8a6d
- https://git.kernel.org/stable/c/945d9894502cd9124f5d676181c542ed2000f7c0
- https://git.kernel.org/stable/c/9b1a02e0d980ac6b0e36a90378f847062f81d7e4
- https://git.kernel.org/stable/c/b8278ff605187ef3fa0f2705e93251cce4c4f8ee
- https://git.kernel.org/stable/c/b88a511308779c225005d7994b8744561bdbafbc
- https://git.kernel.org/stable/c/cb6abc584a1bfab107ac003d64948a4aef1730aa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72126.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72126
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
