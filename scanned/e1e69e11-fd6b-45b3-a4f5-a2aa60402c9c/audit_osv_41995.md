# [H] svcrdma: wake sq waiters when the transport closes

## Summary
Severity: High
Advisory: CVE-2026-64281
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64281
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

svcrdma: wake sq waiters when the transport closes

Threads parked in svc_rdma_sq_wait() on sc_sq_ticket_wait or
sc_send_wait can hang indefinitely in TASK_UNINTERRUPTIBLE state
across transport teardown, pinning svc_xprt references and
blocking svc_rdma_free().

The close path sets XPT_CLOSE before invoking xpo_detach and both
wait_event predicates include an XPT_CLOSE term, but the
predicates are re-evaluated only on wakeup. sc_sq_ticket_wait has
no completion-driven wake path; it is advanced solely by the
chained ticket handoff inside svc_rdma_sq_wait() itself. Without
an explicit wake at close, parked threads never observe
XPT_CLOSE, hold their svc_xprt_get reference forever, and
svc_rdma_free() blocks on xpt_ref dropping to zero.

Two close entry points reach this transport. Local teardown runs
svc_rdma_detach() from svc_handle_xprt() -> svc_delete_xprt() ->
xpo_detach() on a worker thread. A remote disconnect arrives at
svc_rdma_cma_handler(), which calls svc_xprt_deferred_close():
that sets XPT_CLOSE and enqueues the transport but does not
access either RDMA waitqueue, so a worker already parked in
svc_rdma_sq_wait() never re-evaluates its predicate. With every
worker parked on this transport, no thread is available to run
the local teardown either, and the wake site there is
unreachable.

Introduce svc_rdma_xprt_deferred_close(), a thin svcrdma wrapper
that calls svc_xprt_deferred_close() and then wakes both
sc_sq_ticket_wait and sc_send_wait. Convert the svcrdma producers
that called svc_xprt_deferred_close() directly:
svc_rdma_cma_handler(), qp_event_handler(),
svc_rdma_post_send_err(), svc_rdma_wc_send(), the sendto drop
path, the rw completion error paths, and the recvfrom flush and
read-list error paths.

Wake both waitqueues from svc_rdma_detach() as well. The
synchronous svc_xprt_close() path (backchannel ENOTCONN, device
removal via svc_rdma_xprt_done) reaches detach without flowing
through svc_xprt_deferred_close() and therefore does not invoke
the new helper.

[ cel: add svc_rdma_xprt_deferred_close() to complete the fix ]

## References
- https://git.kernel.org/stable/c/40eedc4253dbda0b29b7961200534dfcecb48ace
- https://git.kernel.org/stable/c/e5248a7426030db1e126363f72afdb3b71339a5c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64281.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64281
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
