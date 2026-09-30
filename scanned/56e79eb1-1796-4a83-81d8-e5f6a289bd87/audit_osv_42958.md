# [C] sunrpc: pin svc_xprt across the asynchronous TLS handshake callback

## Summary
Severity: Critical
Advisory: CVE-2026-72222
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72222
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

sunrpc: pin svc_xprt across the asynchronous TLS handshake callback

svc_tcp_handshake() stores the raw svc_xprt pointer in
tls_handshake_args.ta_data and submits the request through
tls_server_hello_x509(). The handshake core takes only
sock_hold(req->hr_sk); nothing references the embedding struct
svc_sock that svc_tcp_handshake_done() reaches via container_of().

Two close races leave the in-flight callback writing through a freed
svc_sock. svc_sock_free() calls tls_handshake_cancel() and discards
its return value: a false return means handshake_complete() has
already set HANDSHAKE_F_REQ_COMPLETED but hp_done() may not have
finished, yet svc_sock_free() proceeds to kfree(svsk). The
cancel-loser fall-through inside svc_tcp_handshake() itself produces
the same window: when wait_for_completion_interruptible_timeout()
returns <= 0 (timeout or signal) and tls_handshake_cancel() returns
false, the function does not drain, returns, and svc_handle_xprt()
calls svc_xprt_received(), which clears XPT_BUSY and can drop the
last reference. A concurrent close then runs svc_sock_free() while
svc_tcp_handshake_done() is still updating xpt_flags and walking
svsk->sk_handshake_done.

The corruption surfaces as set_bit/clear_bit RMW into the freed
xpt_flags slab slot and as complete_all() walking and writing the
freed wait_queue_head_t list embedded in sk_handshake_done -- a
slab-corruption primitive, not a benign read. The path is reachable
on any TLS-enabled NFS server whenever a connection close overlaps
the tlshd downcall delivery window; the interruptible wait means
signal delivery suffices, not just SVC_HANDSHAKE_TO expiry.

Take svc_xprt_get(xprt) immediately before tls_server_hello_x509()
so the in-flight callback owns its own reference. Release it on the
two edges where the callback is guaranteed not to fire -- submission
failure from tls_server_hello_x509() and a successful
tls_handshake_cancel() -- and at the tail of
svc_tcp_handshake_done() after complete_all().

[cel: rewrote commit message to describe the actual change]

## References
- https://git.kernel.org/stable/c/083e9c2ec7e8bb13b79c9fd7b337abdd758ecc5f
- https://git.kernel.org/stable/c/2d4f97d13fff91e0bc539216be88b884b544d49f
- https://git.kernel.org/stable/c/3f9ee75a97a769be258784c22b89657acb5ed9bd
- https://git.kernel.org/stable/c/4f988f3a2808fb659f3880c282041ff067acad78
- https://git.kernel.org/stable/c/f3b55945dd99f29d83e1965d0141040a35262346
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72222.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72222
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
