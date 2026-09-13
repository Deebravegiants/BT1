# [H] tipc: serialize udp bearer replicast list updates

## Summary
Severity: High
Advisory: CVE-2026-68323
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68323
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: serialize udp bearer replicast list updates

tipc_udp_rcast_add() and cleanup_bearer() both update ub->rcast.list with
list_add_rcu() / list_del_rcu(), but nothing serializes them. The add runs
from the encap receive softirq (via tipc_udp_rcast_disc()) without
rtnl_lock(), so it can race the cleanup delete and corrupt the list:

  list_del corruption. prev->next should be ffff8880298d7ab8,
    but was ffff88802449ad38. (prev=ffff888027e3ec98)
  kernel BUG at lib/list_debug.c:62!
  RIP: __list_del_entry_valid_or_report+0x17a/0x200
  Workqueue: events cleanup_bearer
  Call Trace:
   cleanup_bearer (net/tipc/udp_media.c:811)
   process_one_work (kernel/workqueue.c:3302)
   worker_thread (kernel/workqueue.c:3466)

The bearer can be enabled from an unprivileged user namespace, as the
TIPCv2 generic-netlink ops carry no GENL_ADMIN_PERM.

Add a spinlock to struct udp_bearer and take it around the list_add_rcu()
in tipc_udp_rcast_add() and the list_del_rcu() loop in cleanup_bearer() so
the two writers can no longer corrupt the list.

Reject a duplicate peer under the same lock before allocating, and remove
tipc_udp_is_known_peer(). The old lockless pre-check in
tipc_udp_rcast_disc() was racy: two softirqs discovering the same peer
could both find it absent and add it twice.

cleanup_bearer() runs from a workqueue after tipc_udp_disable() clears the
bearer's up bit, so an encap softirq can still reach tipc_udp_rcast_add()
and add a peer after cleanup_bearer() has already emptied the list, leaking
that entry when the bearer is freed. Mark the bearer disabled under
rcast_lock once the list is emptied and refuse further additions.

## References
- https://git.kernel.org/stable/c/350e592ff4e30e48ffb55e142d11a73e63f4869c
- https://git.kernel.org/stable/c/d70c81001df9320d3445e664428a1d408b5ba896
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68323.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68323
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
