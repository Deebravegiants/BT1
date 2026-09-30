# [H] tipc: fix use-after-free of the discoverer in tipc_disc_rcv()

## Summary
Severity: High
Advisory: CVE-2026-64543
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-64543
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: fix use-after-free of the discoverer in tipc_disc_rcv()

bearer_disable() frees b->disc with tipc_disc_delete()'s plain kfree(),
but tipc_disc_rcv() still dereferences b->disc in RX softirq under
rcu_read_lock() (tipc_udp_recv -> tipc_rcv -> tipc_disc_rcv).

L2 bearers are safe thanks to the synchronize_net() in
tipc_disable_l2_media(), but the UDP bearer defers that call to the
cleanup_bearer() workqueue, so the discoverer is freed with no grace
period:

 BUG: KASAN: slab-use-after-free in tipc_disc_rcv (net/tipc/discover.c:149)
 Read of size 8 at addr ffff88802348b728 by task poc_tipc/184
 <IRQ>
  tipc_disc_rcv (net/tipc/discover.c:149)
  tipc_rcv (net/tipc/node.c:2126)
  tipc_udp_recv (net/tipc/udp_media.c:391)
  udp_rcv (net/ipv4/udp.c:2643)
  ip_local_deliver_finish (net/ipv4/ip_input.c:241)
 </IRQ>
 Freed by task 181:
  kfree (mm/slub.c:6565)
  bearer_disable (net/tipc/bearer.c:418)
  tipc_nl_bearer_disable (net/tipc/bearer.c:1001)

The bearer is freed with kfree_rcu(); free the discoverer the same way.
Add an rcu_head to struct tipc_discoverer and free it and its skb from an
RCU callback.

Because the RCU callback (tipc_disc_free_rcu) lives in module text, a
call_rcu() that is still pending when the tipc module is unloaded would
invoke a freed function. Add an rcu_barrier() to tipc_exit() after the
bearer subsystem has been torn down, so all pending discoverer callbacks
have run before the module text goes away.

Reachable from an unprivileged user namespace: the TIPCv2 genl family is
netnsok and its bearer commands have no GENL_ADMIN_PERM. Needs CONFIG_TIPC
and CONFIG_TIPC_MEDIA_UDP.

## References
- https://git.kernel.org/stable/c/1579342d71133da7f00daa02c75cebec7372097b
- https://git.kernel.org/stable/c/380413cdfd29fb9fa486c82889132b680c4983c5
- https://git.kernel.org/stable/c/4da2ac7749411971e1b222b992da5a172ce45f98
- https://git.kernel.org/stable/c/5e215bf1c47fdddf8203a0fe80a0ed594065f101
- https://git.kernel.org/stable/c/a0c5fdeb5fa257f8c6d469af266bc087cb5de6a2
- https://git.kernel.org/stable/c/b65289e1c3f352a9f92c6e19713ddd647e033253
- https://git.kernel.org/stable/c/ec7d54d8cc1723921d671e3272b427c96366506f
- https://git.kernel.org/stable/c/f05b3f4c78370469286879c765f5a1dd39dbcd32
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64543.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64543
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
