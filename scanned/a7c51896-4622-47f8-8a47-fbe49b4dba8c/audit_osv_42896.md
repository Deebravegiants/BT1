# [H] can: bcm: fix stale rx/tx ops after device removal

## Summary
Severity: High
Advisory: CVE-2026-72116
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72116
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.25 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: bcm: fix stale rx/tx ops after device removal

RX: an RX_SETUP update(!) for an existing op skipped can_rx_register()
unconditionally, even when a concurrent NETDEV_UNREGISTER had already
torn down its registration (op->rx_reg_dev == NULL). This silently
did not re-enable frame delivery for that updated filter. bcm_rx_setup()
now re-registers in that case, while leaving rx_ops with ifindex = 0
(all CAN devices) which never carry a tracked rx_reg_dev registered as-is.

TX: bcm_notify() only handled bo->rx_ops on NETDEV_UNREGISTER, leaving
tx_ops with an active cyclic transmission re-arming its hrtimer
indefinitely to execute bcm_tx_timeout_handler(). Cancelling the hrtimer
prevents the runaway timer and any injection into a later reused ifindex,
since nothing else calls bcm_can_tx() for the op until an explicit
TX_SETUP update re-arms it.

Unlike bcm_rx_unreg(), which clears the tracked rx_reg_dev for rx_ops,
the ifindex is intentionally left unchanged for tx_ops. bcm_tx_setup()
always rejects ifindex 0, so clearing it would strand the op: neither a
later TX_SETUP (bcm_find_op()) nor TX_DELETE (bcm_delete_tx_op()) could
ever find it again, since both require an exact ifindex match.

## References
- https://git.kernel.org/stable/c/3b762c0d950383ab7a002686c9136b9aa55d2d70
- https://git.kernel.org/stable/c/60d8a7942f4ed2d975207aaeba1adb576707e53d
- https://git.kernel.org/stable/c/6be3e1fedf03eab36a2c09d755d1171287b2014b
- https://git.kernel.org/stable/c/9517d8fb0b191398d35b9b7f8c719c1cc7761cb1
- https://git.kernel.org/stable/c/b31d0933509c5a35c0be5736a2ce8df0d1bf112c
- https://git.kernel.org/stable/c/ca829677ffa2de5d79e06366e19ac1e4f5cc78dd
- https://git.kernel.org/stable/c/d30a36066ed3abefb72ae18901f71841ba18b350
- https://git.kernel.org/stable/c/f749e4564952d60e96930c09f2be99955d07c22e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72116.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72116
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
