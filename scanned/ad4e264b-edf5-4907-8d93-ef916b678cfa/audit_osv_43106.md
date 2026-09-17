# [C] xprtrdma: Fix bcall rep leak and unbounded peek

## Summary
Severity: Critical
Advisory: CVE-2026-72466
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72466
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

xprtrdma: Fix bcall rep leak and unbounded peek

rpcrdma_is_bcall() decodes a reply's first words to decide whether
the frame is a backchannel call. Two issues in that decode path
let a short or malformed reply leak the receive buffer and drain
the Receive queue.

First, the speculative peek

    p = xdr_inline_decode(xdr, 0);
    /* five p++ reads follow */

asks xdr_inline_decode() for zero bytes, which returns xdr->p
without consulting xdr->end. The five subsequent __be32 reads can
then walk up to 20 bytes past the wire payload into stale regbuf
contents and misclassify the reply as a backchannel call.

Second, after the post-peek

    p = xdr_inline_decode(xdr, 3 * sizeof(*p));
    if (unlikely(!p))
            return true;

the short-header arm returns true without calling
rpcrdma_bc_receive_call(). The contract with the caller is that a
true return transfers ownership of rep to the backchannel path:

    rpcrdma_reply_handler()
      if (rpcrdma_is_bcall(r_xprt, rep))
              return;        /* bare return, skips out_post */
      ...
    out_post:
      rpcrdma_post_recvs(r_xprt, credits + ...);

Because rpcrdma_bc_receive_call() never ran, no one took rep, but
rpcrdma_reply_handler still bare-returns past rpcrdma_rep_put()
and rpcrdma_post_recvs(). The rep, with its persistently
DMA-mapped receive buffer, is orphaned on rb_all_reps and freed
only at transport teardown. This completion reposts nothing, so
its slot is reclaimed only when a later forward-channel reply
reaches out_post and rpcrdma_post_recvs() allocates a fresh rep to
backfill; absent that traffic the Receive queue drains and the
peer's Sends draw RNR NAKs.

Fix by consulting xdr->end after the zero-length peek so the five
__be32 reads cannot run unless 20 bytes of wire payload remain. A
byte-precise comparison against xdr->end is required because a
non-4-aligned receive rounds the stream's word count up past the
true payload. Also return false from the short-header arm so the
reply falls through the normal out_norqst cleanup chain
(rpcrdma_rep_put() plus rpcrdma_post_recvs()).

## References
- https://git.kernel.org/stable/c/07aa506436be7634e381e1e1f6d0efa9efc81ecc
- https://git.kernel.org/stable/c/0cee8f9c3b14bd6dee9c4310090a7f45b89b834f
- https://git.kernel.org/stable/c/118a16a18c59f7ad8084b2d13988839b669fca10
- https://git.kernel.org/stable/c/7afc2f8d2fd9394724df9eaf22ce7a71029a5fba
- https://git.kernel.org/stable/c/88b5346284a184a6b7d019912232a571d672d3e3
- https://git.kernel.org/stable/c/c7653d5cebc8492c77ec0415b5e9c0fb3e644bc6
- https://git.kernel.org/stable/c/d7a2870dde3bb09d51d6b9c877642996ad6b92dd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72466.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72466
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
