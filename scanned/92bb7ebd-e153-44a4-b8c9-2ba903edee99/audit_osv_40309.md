# [H] xfrm: espintcp: do not reuse an in-progress partial send

## Summary
Severity: High
Advisory: CVE-2026-52935
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52935
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: espintcp: do not reuse an in-progress partial send

espintcp keeps a single in-flight transmit in ctx->partial.
Before building a new sk_msg, espintcp_sendmsg() first tries to flush
that state through espintcp_push_msgs().

For blocking callers, espintcp_push_msgs() may return success even when
the previous partial send is still pending. espintcp_sendmsg() would
then reinitialize emsg->skmsg and reuse ctx->partial while the old
transfer still owns that state.

Do not rebuild the send message when ctx->partial is still in progress.
If espintcp_push_msgs() returns with emsg->len still set, fail the new
send instead of overwriting the live partial state.

This is a memory-safety fix: reusing the live partial-send state can
leave a stale offset attached to a new sk_msg and lead to an out-of-
bounds read in the send path.

tcp_sendmsg_locked() already handles waiting for send buffer memory, so
the fix here is just to preserve espintcp's one-message-at-a-time
transmit state.

## References
- https://git.kernel.org/stable/c/1777ceac4bea5e568a5ad44b7f9bb219c1db21b6
- https://git.kernel.org/stable/c/37487d55bf3300e3d2c1368da5c2bd3e3834ea4f
- https://git.kernel.org/stable/c/6564e9c7af7e1dc7bfe7f3093b728abe484d7630
- https://git.kernel.org/stable/c/8c6c691bf062dc0753a139a4ab8cb92a70fcf8f3
- https://git.kernel.org/stable/c/aa82a078f70f7ff88ba7d1017134e79d1ac140f2
- https://git.kernel.org/stable/c/ba21439302db9a82fe4edbed1e38a97271529421
- https://git.kernel.org/stable/c/c381039ade2e161ab08c0eda73c4f8b9a7115928
- https://git.kernel.org/stable/c/f9b38a8fbfa07f1deaf7ee1eb38fa8b21ea13990
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52935.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52935
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
