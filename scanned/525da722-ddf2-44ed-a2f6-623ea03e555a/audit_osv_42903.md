# [H] can: isotp: fix use-after-free race with concurrent NETDEV_UNREGISTER

## Summary
Severity: High
Advisory: CVE-2026-72125
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72125
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: isotp: fix use-after-free race with concurrent NETDEV_UNREGISTER

isotp_release() looked up the bound network device via dev_get_by_index()
using the stored ifindex. During device unregistration the device is
unlisted from the ifindex hash before the NETDEV_UNREGISTER notifier
chain runs, so a concurrent isotp_release() could find no device, skip
can_rx_unregister() entirely, and still proceed to free the socket.
Since isotp_release() had already removed itself from the isotp
notifier list at that point, isotp_notify() would never get a chance to
clean up either, leaving a stale CAN filter that keeps pointing at the
freed socket.

Fix this the same way raw.c already does: hold a tracked reference to
the bound net_device in the socket (so->dev/so->dev_tracker) from
bind() onward instead of re-resolving it from the ifindex, and
serialize bind()/release() with rtnl_lock() so that so->dev is always
consistent with what the NETDEV_UNREGISTER notifier sees. so->dev
stays valid regardless of ifindex-hash unlisting, and is only ever
cleared by whichever of isotp_release()/isotp_notify() gets there
first, so the filter is always removed exactly once.

isotp_bind() now rejects a (re)bind with -EAGAIN while so->[tx|rx].state
isn't ISOTP_IDLE yet, so a timer left running by a prior
NETDEV_UNREGISTER can't act on a newly bound so->ifindex. Both checks
share the same lock_sock() section, so there is no window in which a
concurrent isotp_notify() clearing so->bound could be missed.

## References
- https://git.kernel.org/stable/c/0b811c4bbe3ec9ad611e90a540fe8b51b3bb8a96
- https://git.kernel.org/stable/c/20bab8b88baac140ca3701116e1d486c7f51e311
- https://git.kernel.org/stable/c/33b9cd9245e2a4b800f99ed1cc53d64960614152
- https://git.kernel.org/stable/c/43884dc7963beef2328f507f4fe680bdc173eb80
- https://git.kernel.org/stable/c/7bef39ba76eb7307ed22a50329e0f5776dbeda58
- https://git.kernel.org/stable/c/8e018f4335590460ebcf0c2b493ed38ba1a35204
- https://git.kernel.org/stable/c/e442b62ba5a7756c17e05a77b32cdd085a2b6138
- https://git.kernel.org/stable/c/f311bbb29bb06aaab69ba45a6e4b11323d20b8f9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72125.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72125
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
