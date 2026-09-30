# [H] tipc: read le->link under the node lock in tipc_node_link_down()

## Summary
Severity: High
Advisory: CVE-2026-74609
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74609
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: read le->link under the node lock in tipc_node_link_down()

tipc_node_link_down() caches the link pointer before taking n->lock:

	struct tipc_link *l = le->link;		/* unlocked */

	if (!l)
		return;
	tipc_node_write_lock(n);
	if (!tipc_link_is_establishing(l)) {	/* deref l */
	...
		tipc_link_reset(l);		/* write into l */
	if (delete) {
		kfree(l);
		le->link = NULL;

The delete=true caller frees that very object under n->lock, so the lock
does not protect the cached pointer against it:

 - CPU A, delete=false: tipc_rcv() on TIPC_LINK_DOWN_EVT, or the link
   supervision timer via tipc_node_timeout(), reads l unlocked and then
   dereferences it under n->lock;
 - CPU B, delete=true: netlink TIPC_NL_BEARER_DISABLE -> bearer_disable()
   -> tipc_node_delete_links() -> tipc_node_link_down(n, bearer_id, true)
   -> kfree(l).

The link is freed with plain kfree(), not kfree_rcu(), and for UDP bearers
disable_media() only schedules the asynchronous cleanup_bearer() work, so
its synchronize_net() runs after the links are already gone.  An in-flight
CPU A that has read l therefore dereferences freed memory once B frees it:
a use-after-free read in tipc_link_is_establishing(), and a use-after-free
write via tipc_link_reset() on the establishing branch.

The following trace was captured on 7.2.0-rc5-00284-gaf39eb111ce6:

  BUG: KASAN: slab-use-after-free in tipc_link_is_establishing (net/tipc/link.c:285)
  Read of size 4 at addr ffff88802e2aa068 by task swapper/2/0
   tipc_link_is_establishing (net/tipc/link.c:285)
   tipc_node_link_down (net/tipc/node.c:1076)
   tipc_node_timeout (net/tipc/node.c:843)
  Allocated by task 9549:
   tipc_link_create (net/tipc/link.c:490)
   tipc_node_check_dest (net/tipc/node.c:1279)
   tipc_disc_rcv (net/tipc/discover.c:252)
   tipc_udp_recv (net/tipc/udp_media.c:389)
  Freed by task 9549:
   tipc_node_link_down (net/tipc/node.c:1084)
   tipc_node_delete_links (net/tipc/node.c:1320)
   bearer_disable (net/tipc/bearer.c:414)
   __tipc_nl_bearer_disable (net/tipc/bearer.c:992)

Move the le->link read inside tipc_node_write_lock(), so it is serialised
against the kfree() in the delete path.  A racing teardown now either has
not run yet, and we see a valid link, or has already run, and we see NULL.

## References
- https://git.kernel.org/stable/c/2be741ad565c610871a6a95062c12c39da7168fd
- https://git.kernel.org/stable/c/47ba70891b10b2feb52462086b7fcd2ad75d3ce3
- https://git.kernel.org/stable/c/5558a8312452ddb21eff22b1cbd84302ad951944
- https://git.kernel.org/stable/c/69d209461c110388710e483a130caf051e4fd09a
- https://git.kernel.org/stable/c/a714d62513befef37f71f4ae89bb1fe173b65f2e
- https://git.kernel.org/stable/c/c3f2347a47754eac690967cfd82cb6d559817b07
- https://git.kernel.org/stable/c/cba9ccb47e9fa4cc77692fb896cc5ab57a667882
- https://git.kernel.org/stable/c/de017c22135f545ca4e65d1eada22887b64958eb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74609.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74609
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
