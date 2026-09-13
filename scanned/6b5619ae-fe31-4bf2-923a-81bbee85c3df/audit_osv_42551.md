# [H] wifi: cfg80211: use wiphy work for socket owner autodisconnect

## Summary
Severity: High
Advisory: CVE-2026-68404
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68404
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: cfg80211: use wiphy work for socket owner autodisconnect

nl80211_netlink_notify() walks the cfg80211 wireless device list when a
NETLINK_GENERIC socket is released. If the socket owns a connection, the
notifier queues the embedded wdev->disconnect_wk work item.

That work is a plain work_struct today. NETDEV_GOING_DOWN cancels it, but a
NETLINK_URELEASE notifier that already observed conn_owner_nlportid can
queue it after that cancel returns. _cfg80211_unregister_wdev() then
removes the wdev from the list and waits for RCU readers, but
synchronize_net() does not drain work queued by such a reader.

Make the autodisconnect work a wiphy_work instead. The callback already
needs the wiphy mutex, and wiphy_work runs under that mutex. This lets
teardown cancel pending autodisconnect work while holding the mutex,
without a cancel_work_sync() vs. worker locking concern.

Also cancel the wiphy work after list_del_rcu() and synchronize_net(). Any
NETLINK_URELEASE notifier that had already reached the wdev list has then
either queued the work and it is removed, or can no longer find the wdev.

## References
- https://git.kernel.org/stable/c/0c2ed186bbe14304415476d6707b747dddcd8583
- https://git.kernel.org/stable/c/6d6123fef5a4af175cc6b6b12a03dd0f3c240b79
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68404.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68404
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
