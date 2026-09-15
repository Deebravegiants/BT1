# [C] net/handshake: hand off the pinned file reference to accept_doit

## Summary
Severity: Critical
Advisory: CVE-2026-63979
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63979
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.18.44, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/handshake: hand off the pinned file reference to accept_doit

handshake_req_next() removes the request from the per-net
pending list and drops hn_lock before handshake_nl_accept_doit()
reads req->hr_sk->sk_socket and dereferences sock->file (once in
FD_PREPARE() and again in get_file()).  In that window a
consumer running tls_handshake_cancel() followed by sockfd_put()
(svc_sock_free) or __fput_sync() (xs_reset_transport) releases
sock->file.  sock_release() then runs sock_orphan(), zeroing
sk_socket, and frees the struct socket.  The accept-side code
either reads NULL through sk_socket or chases freed memory.

The submit-side sock_hold() does not prevent this.  sk_refcnt
protects struct sock, but struct socket and sock->file are
independently refcounted via the file descriptor the consumer
owns.  Pinning sk leaves sock and sock->file unprotected.

Retarget the accept-side dereferences at req->hr_file, which was
pinned at submit time, instead of req->hr_sk->sk_socket->file.
Pinning on its own is not sufficient: a consumer that cancels
between handshake_req_next() returning and accept_doit reaching
FD_PREPARE() takes the !remove_pending() branch in
handshake_req_cancel() and drops hr_file before the accept side
takes its own reference.  Hand off an additional file reference
inside handshake_req_next(), under hn_lock, so the accept side
operates on a reference that no concurrent handshake_req_cancel()
can revoke.  FD_PREPARE() consumes that handed-off reference,
either by transferring it to the new fd in fd_publish() or by
dropping it in the cleanup destructor on error; the explicit
get_file() that previously balanced FD_PREPARE() is therefore
redundant and goes away.

Update handshake_req_cancel_test2 and _test3 to simulate the
FD_PREPARE() consumption with an fput() so the kunit file-count
assertions stay balanced.

## References
- https://git.kernel.org/stable/c/68eba6519cbd6359fb554a9720f3a3b6b2eba23f
- https://git.kernel.org/stable/c/c06876d4fac38f35820946ee3b1be7d7da799cd4
- https://git.kernel.org/stable/c/f4251190e58b209999c1ba9e6d2976136a1be055
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63979.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63979
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
