# [H] ovpn: tcp - use cached peer pointer in ovpn_tcp_close()

## Summary
Severity: High
Advisory: CVE-2026-64045
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64045
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ovpn: tcp - use cached peer pointer in ovpn_tcp_close()

ovpn_tcp_close() loads the ovpn_socket via rcu_dereference_sk_user_data()
under rcu_read_lock(), takes a reference on sock->peer, caches the peer
pointer in a local, and drops the read lock. It then passes sock->peer
(rather than the cached local) to ovpn_peer_del(), re-dereferencing the
ovpn_socket after the RCU read section has ended.

Unlike ovpn_tcp_sendmsg(), which uses the same "load under RCU, use
after unlock" pattern but is protected by lock_sock() held across the
function, ovpn_tcp_close() runs without the socket lock: inet_release()
invokes sk_prot->close() without taking lock_sock first.

ovpn_socket_release() can therefore complete its kref_put -> detach ->
synchronize_rcu -> kfree(sock) sequence concurrently, in the window
after ovpn_tcp_close() drops rcu_read_lock() but before it dereferences
sock->peer. The synchronize_rcu() in ovpn_socket_release() protects
readers that use the dereferenced pointer inside the RCU read section,
not those that escape the pointer to a local and use it afterwards.

A reproducer follows the pattern of commit 94560267d6c4 ("ovpn: tcp -
don't deref NULL sk_socket member after tcp_close()"): trigger a peer
removal (keepalive expiration or netlink OVPN_CMD_DEL_PEER) at the same
moment userspace closes the TCP fd. That commit fixed the detach-side
of the same race window; this one fixes the close-side at a different
victim.

Tighten the entry block to read sock->peer exactly once into the cached
peer local, and route all subsequent uses (the hold check, the
ovpn_peer_del() call, and the prot->close() invocation) through that
local. sock->peer is only ever written once in ovpn_socket_new() under
lock_sock(), before rcu_assign_sk_user_data() publishes the ovpn_socket,
and is never reassigned afterwards - but the previous multi-read pattern
made that invariant implicit rather than explicit. The same multi-read
shape exists in ovpn_tcp_recvmsg(), ovpn_tcp_sendmsg(),
ovpn_tcp_data_ready() and ovpn_tcp_write_space(); those will be cleaned
up via a dedicated helper in a follow-up net-next series.

## References
- https://git.kernel.org/stable/c/775d8d7ad02aa345e1588424a6a8b9ae49fb9012
- https://git.kernel.org/stable/c/d3ef441907fca7c340979e577a3db3bb634bf166
- https://git.kernel.org/stable/c/e5460eb7238c19d651a9b22b2378b587033a4095
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64045.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64045
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
