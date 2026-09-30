# [H] tcp: call sk_data_ready() after listener migration

## Summary
Severity: High
Advisory: CVE-2026-46015
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46015
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.86, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: call sk_data_ready() after listener migration

When inet_csk_listen_stop() migrates an established child socket from
a closing listener to another socket in the same SO_REUSEPORT group,
the target listener gets a new accept-queue entry via
inet_csk_reqsk_queue_add(), but that path never notifies the target
listener's waiters. A nonblocking accept() still works because it
checks the queue directly, but poll()/epoll_wait() waiters and
blocking accept() callers can also remain asleep indefinitely.

Call READ_ONCE(nsk->sk_data_ready)(nsk) after a successful migration
in inet_csk_listen_stop().

However, after inet_csk_reqsk_queue_add() succeeds, the ref acquired
in reuseport_migrate_sock() is effectively transferred to
nreq->rsk_listener. Another CPU can then dequeue nreq via accept()
or listener shutdown, hit reqsk_put(), and drop that listener ref.
Since listeners are SOCK_RCU_FREE, wrap the post-queue_add()
dereferences of nsk in rcu_read_lock()/rcu_read_unlock(), which also
covers the existing sock_net(nsk) access in that path.

The reqsk_timer_handler() path does not need the same changes for two
reasons: half-open requests become readable only after the final ACK,
where tcp_child_process() already wakes the listener; and once nreq is
visible via inet_ehash_insert(), the success path no longer touches
nsk directly.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/12625b4da84caf4d84a04988710a7b9bcf702b18
- https://git.kernel.org/stable/c/14e9bb6eba8f59dcc637702e4744ae5e30660d76
- https://git.kernel.org/stable/c/3864c6ba1e041bc75342353a70fa2a2c6f909923
- https://git.kernel.org/stable/c/7aa7933a5607b1e5b56f322d17265c1d0ea02c51
- https://git.kernel.org/stable/c/83bb57635d7cbafde32f865b577ecfd969f02337
- https://git.kernel.org/stable/c/ab5fdcd535645f6dbe6e9e21d96a08d141e88b4b
- https://git.kernel.org/stable/c/bebd058ef40c67a81fe6d9ee8beaa4ede90e0704
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46015.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46015
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
