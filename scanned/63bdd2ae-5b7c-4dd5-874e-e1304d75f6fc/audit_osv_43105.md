# [H] xprtrdma: Sanitize the reply credit grant after parsing

## Summary
Severity: High
Advisory: CVE-2026-72465
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72465
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

xprtrdma: Sanitize the reply credit grant after parsing

The out_norqst exit in rpcrdma_reply_handler() branches away before
the credit clamp, so a reply that matches no pending request reaches
out_post carrying the raw credit value parsed from the wire.
rpcrdma_post_recvs() does not bound its @needed argument: the refill
loop allocates and chains Receive WRs until the count is satisfied or
allocation fails. A peer that sends a well-formed reply carrying an
unknown XID and an inflated credit grant therefore drives rep
allocation and Receive posting past re_max_requests on every such
reply.

Move the clamp to immediately after the credit field is parsed,
ahead of the first branch that can reach out_post, so every later
consumer sees a sanitized value. The cwnd update stays on the
matched-request path.

## References
- https://git.kernel.org/stable/c/33db78b1b24fc6a464ae08aa4d2538c5f883eb5e
- https://git.kernel.org/stable/c/41634242140173eabbf54f899f9c70b5c685e786
- https://git.kernel.org/stable/c/469b22376ee73369711ecf2761bd122ef4195963
- https://git.kernel.org/stable/c/7cf332b3d82d73ffceedca6b4a120be074172021
- https://git.kernel.org/stable/c/8be1bb378def94a5cb8f7527a191e476407118ec
- https://git.kernel.org/stable/c/c3a628aab2dc8f5fd7bff86ceaeae64de590e60a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72465.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72465
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
