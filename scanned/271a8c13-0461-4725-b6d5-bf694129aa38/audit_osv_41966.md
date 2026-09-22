# [H] Bluetooth: L2CAP: cancel pending_rx_work before taking conn->lock

## Summary
Severity: High
Advisory: CVE-2026-64206
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-64206
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.16.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: L2CAP: cancel pending_rx_work before taking conn->lock

l2cap_conn_del() takes conn->lock and then calls cancel_work_sync() for
pending_rx_work.  process_pending_rx() takes the same mutex, so teardown
can deadlock against the worker it is flushing.

This issue was found by our static analysis tool and then manually
reviewed against the current tree.

The grounded PoC kept the l2cap_conn_ready() -> queue_work(...,
&conn->pending_rx_work) submit path, the l2cap_conn_del() ->
cancel_work_sync(&conn->pending_rx_work) teardown path, and the
process_pending_rx() -> mutex_lock(&conn->lock) worker edge.  Lockdep

  WARNING: possible circular locking dependency detected
  process_pending_rx+0x21/0x2a [vuln_msv]
  l2cap_conn_del.constprop.0+0x3f/0x4e [vuln_msv]
  *** DEADLOCK ***

Cancel pending_rx_work before taking conn->lock, matching the existing
lock-before-drain ordering used for the two delayed works in the same
teardown path.  The pending_rx queue is still purged after the work has
been cancelled and conn->lock has been acquired.

## References
- https://git.kernel.org/stable/c/2641a9e0a1dd4af2e21995470a21d55dd35e5203
- https://git.kernel.org/stable/c/4a0bb0fd63fe2b0c62e1072cd1811d6f61e0081c
- https://git.kernel.org/stable/c/8daaf7f73fe998631a160d1a5a7e1b0b0480eef8
- https://git.kernel.org/stable/c/8de7b386ffad480ca59222b688c94a2da8f0d805
- https://git.kernel.org/stable/c/9901f847a762a5d953871dd95767ce2aed3d684d
- https://git.kernel.org/stable/c/d5616beb3355b5fca2280d796c1cf7ada4ee6551
- https://git.kernel.org/stable/c/e96fbac8d3a73b0bc165383c092a30628561d320
- https://git.kernel.org/stable/c/fc0c3b9cf27cfa2a06f66dae1d08c668fe0a2faa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64206.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64206
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
