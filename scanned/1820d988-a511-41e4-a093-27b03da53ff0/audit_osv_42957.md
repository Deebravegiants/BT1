# [C] sunrpc: wait for in-flight TLS handshake callback when cancel loses race

## Summary
Severity: Critical
Advisory: CVE-2026-72221
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72221
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

sunrpc: wait for in-flight TLS handshake callback when cancel loses race

When wait_for_completion_interruptible_timeout() in
svc_tcp_handshake() returns 0 (timeout) or -ERESTARTSYS (signal) and
tls_handshake_cancel() then returns false, handshake_complete() has
won the cancellation race: it has set HANDSHAKE_F_REQ_COMPLETED and
is about to invoke svc_tcp_handshake_done(), but the callback's
side effects on xpt_flags and on svsk->sk_handshake_done have not
yet committed.

The current code reads xpt_flags immediately to decide whether the
session succeeded. Two races result.

If the callback has executed set_bit(XPT_TLS_SESSION) but not yet
clear_bit(XPT_HANDSHAKE), svc_tcp_handshake() sees a session,
enqueues the transport, and returns. svc_xprt_received() then
clears XPT_BUSY, a worker thread picks the transport up, the
dispatcher in svc_handle_xprt() observes XPT_HANDSHAKE still set,
and xpo_handshake is invoked a second time. That svc_tcp_handshake()
calls init_completion(&svsk->sk_handshake_done) while the original
callback concurrently calls complete_all() on it, corrupting the
embedded swait_queue.

If the callback has set HANDSHAKE_F_REQ_COMPLETED but not yet
entered svc_tcp_handshake_done(), svc_tcp_handshake() reads
XPT_TLS_SESSION as clear and tears the connection down even though
the handshake is about to succeed.

Wait for the callback to commit before inspecting xpt_flags. The
completion is guaranteed to fire because handshake_complete()
invokes svc_tcp_handshake_done() unconditionally once it has set
HANDSHAKE_F_REQ_COMPLETED.

## References
- https://git.kernel.org/stable/c/0d8ceb39884148dc7a2fdf71e1cac5961ed1d2b9
- https://git.kernel.org/stable/c/65b23bec1fca6e9ebdc3e6041ebf8c6ab074141b
- https://git.kernel.org/stable/c/a4f878e8ecd729ccf2e50993444e217583adeace
- https://git.kernel.org/stable/c/d00e32f84ca1a77cb67a3fbf59f58dada95f5a21
- https://git.kernel.org/stable/c/e0f4691d42a54d359d8b64509fd9ab938d4f2a33
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72221.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72221
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
