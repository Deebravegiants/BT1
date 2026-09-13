# [H] ovpn: run deferred work on a module-owned workqueue

## Summary
Severity: High
Advisory: CVE-2026-80753
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-80753
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.50, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ovpn: run deferred work on a module-owned workqueue

ovpn queues several work items whose callbacks execute module text.
These works currently run on the global system workqueues, so module
exit has no driver-owned drain point that guarantees the callbacks have
fully returned before the module text can be freed.

Object references protect the objects used by the callbacks, but they do
not prove that a workqueue function has returned. In particular, a
worker can drop the final reference that unblocks device teardown while
it is still executing ovpn code.

Add a module-owned workqueue and queue all ovpn work items on it. During
module exit, unregister rtnl and netlink first, flush the workqueue so
ordinary ovpn workers finish, run the final RCU barrier, and destroy the
workqueue last. This keeps the workqueue available for cleanup work
queued from RCU callbacks, while ensuring no ovpn work item can outlive
the module text.

The per-device delayed keepalive work remains explicitly disabled during
netdev teardown (disable_delayed_work_sync in ndo_uninit), since
flush_workqueue does not flush delayed work that is still only pending
on its timer.

## References
- https://git.kernel.org/stable/c/b5fe67111e63a8a81ec31056c4475509076fd266
- https://git.kernel.org/stable/c/bbe81f40582d451ac849b20707784220f33a23bd
- https://git.kernel.org/stable/c/e9714db8041763f59dde152c812b96b3de05c6d9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80753.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80753
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
