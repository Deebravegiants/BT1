# [H] tipc: fix UAF in cleanup_bearer() due to premature dst_cache_destroy()

## Summary
Severity: High
Advisory: CVE-2026-72404
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72404
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: fix UAF in cleanup_bearer() due to premature dst_cache_destroy()

TIPC UDP media bearer teardown calls dst_cache_destroy() on its
replicast caches before calling synchronize_net() to wait for
concurrent RCU readers (transmitters) to finish:

static void cleanup_bearer(struct work_struct *work)
{
...
	list_for_each_entry_safe(rcast, tmp, &ub->rcast.list, list) {
		dst_cache_destroy(&rcast->dst_cache);
		list_del_rcu(&rcast->list);
		kfree_rcu(rcast, rcu);
	}
...
	dst_cache_destroy(&ub->rcast.dst_cache);
	udp_tunnel_sock_release(ub->sk);
	synchronize_net();
...
}

This is highly buggy because dst_cache_destroy() immediately frees the
per-CPU cache memory (free_percpu()) and releases the cached dst
entries without any synchronization.

If a concurrent transmitter (e.g., tipc_udp_xmit()) is running on another
CPU under RCU protection, it can call dst_cache_get() concurrently,
leading to:
1. Use-After-Free on the per-CPU cache pointer itself (crash).
2. "rcuref - imbalanced put()" warning if it attempts to release a
   dst that was concurrently released by dst_cache_destroy().

Furthermore, calling kfree(ub) immediately after synchronize_net() without
closing the socket first (or waiting after closing it) leaves a window
where a concurrent receiver (tipc_udp_recv()) could start after
synchronize_net(), access ub, and suffer a UAF when kfree(ub) runs.

To fix this, we must defer dst_cache_destroy() and kfree(ub) until after
we have ensured that no more readers can see the bearer/socket and all
existing readers have finished:

1. Defer rcast entry destruction (both dst_cache_destroy() and kfree())
   to an RCU callback using call_rcu_hurry().
   Using call_rcu_hurry() ensures the dst entries are released quickly.

2. Release the bearer socket using udp_tunnel_sock_release() (stops
   new receive readers).

3. Call synchronize_net() to wait for all outstanding RCU readers
   (both transmit and receive) to finish.

4. Now that it is safe, call dst_cache_destroy() on the main bearer
   cache, and free ub.

Note: 3) and 4) can be changed later in net-next to also use
call_rcu_hurry() and get rid of the synchronize_net() latency.

## References
- https://git.kernel.org/stable/c/1c8393eefa3cadf4ca0b61119ad1321aa32d3c8c
- https://git.kernel.org/stable/c/7116764ca53ff529335d7ab7c364a69f094b23a5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72404.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72404
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
