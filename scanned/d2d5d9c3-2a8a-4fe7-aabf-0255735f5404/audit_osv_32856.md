# [H] af_packet: move notifier's packet_dev_mc out of rcu critical section

## Summary
Severity: High
Advisory: CVE-2025-38150
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-03
Source: https://osv.dev/vulnerability/CVE-2025-38150
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

af_packet: move notifier's packet_dev_mc out of rcu critical section

Syzkaller reports the following issue:

 BUG: sleeping function called from invalid context at kernel/locking/mutex.c:578
 __mutex_lock+0x106/0xe80 kernel/locking/mutex.c:746
 team_change_rx_flags+0x38/0x220 drivers/net/team/team_core.c:1781
 dev_change_rx_flags net/core/dev.c:9145 [inline]
 __dev_set_promiscuity+0x3f8/0x590 net/core/dev.c:9189
 netif_set_promiscuity+0x50/0xe0 net/core/dev.c:9201
 dev_set_promiscuity+0x126/0x260 net/core/dev_api.c:286 packet_dev_mc net/packet/af_packet.c:3698 [inline]
 packet_dev_mclist_delete net/packet/af_packet.c:3722 [inline]
 packet_notifier+0x292/0xa60 net/packet/af_packet.c:4247
 notifier_call_chain+0x1b3/0x3e0 kernel/notifier.c:85
 call_netdevice_notifiers_extack net/core/dev.c:2214 [inline]
 call_netdevice_notifiers net/core/dev.c:2228 [inline]
 unregister_netdevice_many_notify+0x15d8/0x2330 net/core/dev.c:11972
 rtnl_delete_link net/core/rtnetlink.c:3522 [inline]
 rtnl_dellink+0x488/0x710 net/core/rtnetlink.c:3564
 rtnetlink_rcv_msg+0x7cf/0xb70 net/core/rtnetlink.c:6955
 netlink_rcv_skb+0x219/0x490 net/netlink/af_netlink.c:2534

Calling `PACKET_ADD_MEMBERSHIP` on an ops-locked device can trigger
the `NETDEV_UNREGISTER` notifier, which may require disabling promiscuous
and/or allmulti mode. Both of these operations require acquiring
the netdev instance lock.

Move the call to `packet_dev_mc` outside of the RCU critical section.
The `mclist` modifications (add, del, flush, unregister) are protected by
the RTNL, not the RCU. The RCU only protects the `sklist` and its
associated `sks`. The delayed operation on the `mclist` entry remains
within the RTNL.

## References
- https://git.kernel.org/stable/c/2dd4781c5af99415ebbd2f7cc763feb109863c05
- https://git.kernel.org/stable/c/d8d85ef0a631df9127f202e6371bb33a0b589952
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38150.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38150
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
