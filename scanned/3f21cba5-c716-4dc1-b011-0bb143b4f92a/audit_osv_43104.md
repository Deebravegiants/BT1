# [H] xprtrdma: Repost Receive buffers for malformed replies

## Summary
Severity: High
Advisory: CVE-2026-72464
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72464
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

xprtrdma: Repost Receive buffers for malformed replies

rpcrdma_wc_receive() decrements the transport's Receive count for
every completion before it dispatches a successful Receive to
rpcrdma_reply_handler(). The handler must post a replacement
Receive WR before returning unless ownership of the rep has moved
elsewhere, as on the backchannel path.

Commit 2ae50ad68cd7 ("xprtrdma: Close window between waking RPC
senders and posting Receives") moved the Receive refill out of
rpcrdma_wc_receive(), where it had run ahead of every reply, into
rpcrdma_reply_handler() so that the responder's credit grant could
be parsed before reposting. The bad-version and short-reply exits
never reach that refill: they recycle the rep and return without
calling rpcrdma_post_recvs().

A remote peer can therefore drain the client's posted Receive
queue by sending a sustained stream of replies that are shorter
than the fixed transport header or that carry an unrecognized
RPC/RDMA version. Each such reply consumes one posted Receive
without replacing it. Once the queue empties, the peer's next
Send finds no posted Receive and the transport stalls until
reconnect.

Route both malformed-reply exits through the shared repost tail
after recycling the rep, refilling against buf->rb_credits, the
most recent accepted credit grant. Neither exit updates the
congestion window, so RPCs admitted under the previous grant
remain in flight awaiting replies. A smaller refill target would
let a stream of malformed replies ratchet the posted Receive count
down to the batch floor while the congestion window still admits
rb_credits RPCs; a burst of valid replies to those RPCs could then
overrun the posted Receives, and because the client connects with
rnr_retry_count of zero, a single RNR NAK terminates the
connection. Refilling against rb_credits also restores the target
that applied to malformed replies before commit 2ae50ad68cd7
("xprtrdma: Close window between waking RPC senders and posting
Receives") when rpcrdma_post_recvs() computed it from rb_credits
internally. rb_credits is at least one from connection
establishment onward, so the repost path always keeps Receives
posted.

## References
- https://git.kernel.org/stable/c/007b4da2f38dcc16a13265416f4ca9f179bab610
- https://git.kernel.org/stable/c/19fae02b272ee4bcdfb5db57f402d28f1697167a
- https://git.kernel.org/stable/c/4322fd9645ee769ad29ce5caea74a1cd9b17269d
- https://git.kernel.org/stable/c/abc011ddaf1617e3e82d8a1e87daa7ddbfb9bac5
- https://git.kernel.org/stable/c/d7c531ab477ae94fd03771d707fd29c787408039
- https://git.kernel.org/stable/c/ef6fb8a5c521f1a07f85202d13e8f2898f247362
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72464.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72464
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
