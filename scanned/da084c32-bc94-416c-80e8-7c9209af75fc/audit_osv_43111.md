# [C] xprtrdma: Decouple req recycling from RPC completion

## Summary
Severity: Critical
Advisory: CVE-2026-72473
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72473
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

xprtrdma: Decouple req recycling from RPC completion

rl_kref formerly served two distinct lifetimes through a single
refcount: it gated when a Reply could wake its RPC task, and it
gated when an rpcrdma_req could return to its free pool. The
marshal path took the Send-side reference only when SGEs needed
DMA-unmap (sc_unmap_count > 0), which made a Send carrying only
pre-registered buffers an exception: the Reply handler dropped
rl_kref from 1 to 0 and freed the req while the HCA might still
be DMA-reading from its send buffer.

Give rl_kref a narrower job. The RPC layer takes one reference
when slot allocation hands a req out. rpcrdma_prepare_send_sges()
takes a Send-side reference unconditionally after WR preparation
succeeds. xprt_rdma_free_slot() and xprt_rdma_bc_free_rqst() drop
the RPC-layer reference; rpcrdma_sendctx_unmap() drops the
Send-side reference. The req returns to its free pool only after
both owners have signed off.

The existing kref_init(&req->rl_kref) call in
rpcrdma_prepare_send_sges() is removed. Initialization moves to
the slot-allocation paths (xprt_rdma_alloc_slot and
rpcrdma_bc_rqst_get), and the release callback re-arms rl_kref
before the req returns to a free pool. A re-init in the marshal
path would discard the RPC-layer reference that already exists
on entry.

Three invariants follow:

  - Any rpcrdma_req held by an rpc_rqst has rl_kref >= 1.
    xprt_rdma_alloc_slot(), rpcrdma_bc_rqst_get(), and the
    backlog-wake branch in xprt_rdma_alloc_slot() each kref_init
    rl_kref before publishing the req. Without this invariant,
    an RPC task that aborts between slot allocation and marshal
    (gss_refresh failure or signal during call_connect, for
    example) would drive xprt_release() ->
    xprt_rdma_free_slot() -> kref_put against a refcount of
    zero, saturating refcount_t and stranding the slot.

  - The Send-side reference is taken only after WR prep
    succeeds. A mapping failure in rpcrdma_prepare_send_sges()
    runs rpcrdma_sendctx_cancel(), which DMA-unmaps the sendctx
    and clears sc_req without touching rl_kref. The sendctx
    ring walks in rpcrdma_sendctx_put_locked() and
    rpcrdma_sendctxs_destroy() skip entries with sc_req == NULL,
    so a burst of -EIO marshal failures cannot hold reqs off
    rb_send_bufs.

  - The release callback re-arms rl_kref so the next consumer
    enters with the invariant satisfied.

Replies now complete the RPC directly. rpcrdma_reply_handler()
calls rpcrdma_complete_rqst() in place of kref_put on the
non-LocalInv branch. The LocalInv branch already completes the
RPC from frwr_unmap_async() and is unaffected.

Because Send-side references can now outlive RPC completion,
connection teardown drains sendctx entries whose unsignaled
Sends never had a later signaled completion to walk the ring.
rpcrdma_sendctxs_destroy() walks the active range and runs
rpcrdma_sendctx_unmap() on each entry with a non-NULL sc_req
before the request buffers are reset, and is moved ahead of
rpcrdma_reqs_reset() in rpcrdma_xprt_disconnect() so the reqs
are still in their pre-reset state when the Send-side refs are
released.

The drain creates a teardown-ordering hazard on the backchannel
path. With the new lifetime, releasing a bc_prealloc req from
rpcrdma_req_release() re-adds it to bc_pa_list. The disconnect
in xprt_rdma_destroy() runs after xprt_destroy_backchannel() has
already emptied bc_pa_list, so the drained reqs would otherwise
leak. xprt_rdma_destroy() now runs xprt_rdma_bc_destroy(xprt, 0)
a second time after the disconnect to reclaim them.

## References
- https://git.kernel.org/stable/c/53442c7d0c888e51b8bc3da196970a669cc6b294
- https://git.kernel.org/stable/c/740975054a1970c0cf15f70ac39724a064f45847
- https://git.kernel.org/stable/c/8203f760a72bd39a3b66bc4eff0aa272a99fe22b
- https://git.kernel.org/stable/c/9f3d9b68c1c6c51746e5ecdb52b2e6a2901de37e
- https://git.kernel.org/stable/c/e7632089523acddcdd8f090ad19e96fb3107b04d
- https://git.kernel.org/stable/c/e786233d2e0bbff9a82e43f02ae3a46ab4b08ec3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72473.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72473
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
