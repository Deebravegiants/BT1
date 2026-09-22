# [C] SUNRPC: pin upper rpc_clnt across the TLS connect_worker

## Summary
Severity: Critical
Advisory: CVE-2026-72317
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72317
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

SUNRPC: pin upper rpc_clnt across the TLS connect_worker

The TLS connect path has a use-after-free: nothing pins the
upper rpc_clnt across the delayed connect_worker. xs_connect()
stores task->tk_client in sock_xprt::clnt as a raw pointer
and queues the worker; for TLS-secured transports that worker
is xs_tcp_tls_setup_socket(), which reads several fields out
of the saved pointer (cl_timeout, cl_program, cl_prog,
cl_vers, cl_cred, cl_stats) to construct the args for the
inner handshake rpc_clnt.

The xprt does not reference the rpc_clnt; the rpc_clnt
references the xprt. xs_destroy() does cancel the
connect_worker, but it runs only when the xprt's refcount
drops to zero, which cannot happen until the rpc_clnt
releases its cl_xprt reference in rpc_free_client_work().
When a TLS handshake fails fatally (for example, an mTLS
mount whose client cert does not match the server), the
connecting task is woken with -EACCES and exits, the mount
caller invokes rpc_shutdown_client(), and the upper rpc_clnt
is freed before the queued connect_worker fires.
xs_tcp_tls_setup_socket() then dereferences the freed clnt,
producing the refcount_t underflow Michael Nemanov reported.

Take a reference on the upper rpc_clnt in xs_connect() for
TLS transports via a new rpc_hold_client() helper, and drop
it in the connect_worker's exit path with rpc_release_client().
The xprt_lock_connect() / xprt_unlock_connect() pairing
already serialises xs_connect() with xs_tcp_tls_setup_socket(),
so the take and release are balanced one-for-one.

The non-TLS connect worker (xs_tcp_setup_socket) never reads
sock_xprt::clnt, so leave that path alone and avoid the
clnt-holds-xprt-holds-clnt cycle that would otherwise prevent
xprt destruction.

## References
- https://git.kernel.org/stable/c/46bc86c833956219bbfd246c1ffd832a479c5199
- https://git.kernel.org/stable/c/5b0427ba582d143a364301f825f4e32272f06d2d
- https://git.kernel.org/stable/c/79cd550f8c884523b604fbfa43eb02def74d6224
- https://git.kernel.org/stable/c/7a65b41b657b71d5a77861f47dd13eb4bc8e10d0
- https://git.kernel.org/stable/c/d49f6d098ed48775b9d27a9f9c5c220fdf76f102
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72317.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72317
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
