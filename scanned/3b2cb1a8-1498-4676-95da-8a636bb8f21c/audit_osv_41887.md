# [H] ovpn: respect peer refcount in CMD_NEW_PEER error path

## Summary
Severity: High
Advisory: CVE-2026-64044
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64044
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ovpn: respect peer refcount in CMD_NEW_PEER error path

ovpn_nl_peer_new_doit()'s error path calls ovpn_peer_release() directly
rather than ovpn_peer_put(), bypassing the kref. The accompanying
comment ("peer was not yet hashed, thus it is not used in any context")
holds for UDP but not for TCP.

For UDP, the ovpn_socket union uses the .ovpn arm and never points back
at a peer; UDP encap_recv looks up peers via the not-yet-populated
hashtables, so the new peer is unreachable until ovpn_peer_add()
publishes it.

For TCP, ovpn_socket_new() sets ovpn_sock->peer and
ovpn_tcp_socket_attach() publishes ovpn_sock via rcu_assign_sk_user_data().
From that moment until ovpn_socket_release() detaches in the error path,
the TCP fd is fully wired: userspace recvmsg / sendmsg / close / poll
on the fd, as well as the strparser-driven ovpn_tcp_rcv() path, can
reach the peer through sk_user_data -> ovpn_sock->peer and bump its
refcount via ovpn_peer_hold().

ovpn_tcp_socket_wait_finish() (called inside ovpn_socket_release())
drains strparser and the tx work, but does not synchronize with
userspace syscall callers that already hold a peer reference. If
ovpn_nl_peer_modify() or ovpn_peer_add() returns an error while such
a caller is in flight - notably an ovpn_tcp_recvmsg() blocked in
__skb_recv_datagram() on peer->tcp.user_queue - the direct
ovpn_peer_release() destroys the peer while the caller still holds
the reference, and the eventual ovpn_peer_put() from that caller
operates on freed memory.

Replace the direct destructor call with ovpn_peer_put() so the kref
correctly defers destruction until the last reference is dropped.
In the common case where no concurrent user is present, behaviour is
unchanged: the kref hits zero immediately and ovpn_peer_release_kref()
runs the same destructor.

With this conversion ovpn_peer_release() has no callers outside peer.c
- ovpn_peer_release_kref() in the same translation unit is the only
remaining user - so make it static and drop its declaration from
peer.h.

## References
- https://git.kernel.org/stable/c/0c3ef71879c0264de6c42463031d9e057da87840
- https://git.kernel.org/stable/c/1fef6614673ff0846d30acdeeaf3cf98bb5f6116
- https://git.kernel.org/stable/c/8298834912d76dbc82c12b6b4ab7590ed2bb8ae5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64044.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64044
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
