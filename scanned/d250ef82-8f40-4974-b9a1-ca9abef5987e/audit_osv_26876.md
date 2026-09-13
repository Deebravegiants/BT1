# [C] SUNRPC: double free xprt_ctxt while still in use

## Summary
Severity: Critical
Advisory: CVE-2023-54269
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54269
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.113, >=5.16.0 <6.1.30, >=5.18.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

SUNRPC: double free xprt_ctxt while still in use

When an RPC request is deferred, the rq_xprt_ctxt pointer is moved out
of the svc_rqst into the svc_deferred_req.
When the deferred request is revisited, the pointer is copied into
the new svc_rqst - and also remains in the svc_deferred_req.

In the (rare?) case that the request is deferred a second time, the old
svc_deferred_req is reused - it still has all the correct content.
However in that case the rq_xprt_ctxt pointer is NOT cleared so that
when xpo_release_xprt is called, the ctxt is freed (UDP) or possible
added to a free list (RDMA).
When the deferred request is revisited for a second time, it will
reference this ctxt which may be invalid, and the free the object a
second time which is likely to oops.

So change svc_defer() to *always* clear rq_xprt_ctxt, and assert that
the value is now stored in the svc_deferred_req.

## References
- https://git.kernel.org/stable/c/7851771789e87108a92697194105ef0c9307dc5e
- https://git.kernel.org/stable/c/e0c648627322a4c7e018e5c7f837c3c03e297dbb
- https://git.kernel.org/stable/c/eb8d3a2c809abd73ab0a060fe971d6b9019aa3c1
- https://git.kernel.org/stable/c/fd86534872f445f54dc01e7db001e25eadf063a8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54269.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54269
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
