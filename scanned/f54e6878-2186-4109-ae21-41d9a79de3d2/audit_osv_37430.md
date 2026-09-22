# [H] media: mediatek: vcodec: fix use-after-free in encoder release path

## Summary
Severity: High
Advisory: CVE-2026-31584
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31584
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14, >=6.20.0 <7.0.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: mediatek: vcodec: fix use-after-free in encoder release path

The fops_vcodec_release() function frees the context structure (ctx)
without first cancelling any pending or running work in ctx->encode_work.
This creates a race window where the workqueue handler (mtk_venc_worker)
may still be accessing the context memory after it has been freed.

Race condition:

    CPU 0 (release path)               CPU 1 (workqueue)
    ---------------------               ------------------
    fops_vcodec_release()
      v4l2_m2m_ctx_release()
        v4l2_m2m_cancel_job()
        // waits for m2m job "done"
                                        mtk_venc_worker()
                                          v4l2_m2m_job_finish()
                                          // m2m job "done"
                                          // BUT worker still running!
                                          // post-job_finish access:
                                        other ctx dereferences
                                          // UAF if ctx already freed
        // returns (job "done")
      kfree(ctx)  // ctx freed

Root cause: The v4l2_m2m_ctx_release() only waits for the m2m job
lifecycle (via TRANS_RUNNING flag), not the workqueue lifecycle.
After v4l2_m2m_job_finish() is called, the m2m framework considers
the job complete and v4l2_m2m_ctx_release() returns, but the worker
function continues executing and may still access ctx.

The work is queued during encode operations via:
  queue_work(ctx->dev->encode_workqueue, &ctx->encode_work)
The worker function accesses ctx->m2m_ctx, ctx->dev, and other ctx
fields even after calling v4l2_m2m_job_finish().

This vulnerability was confirmed with KASAN by running an instrumented
test module that widens the post-job_finish race window. KASAN detected:

  BUG: KASAN: slab-use-after-free in mtk_venc_worker+0x159/0x180
  Read of size 4 at addr ffff88800326e000 by task kworker/u8:0/12

  Workqueue: mtk_vcodec_enc_wq mtk_venc_worker

  Allocated by task 47:
    __kasan_kmalloc+0x7f/0x90
    fops_vcodec_open+0x85/0x1a0

  Freed by task 47:
    __kasan_slab_free+0x43/0x70
    kfree+0xee/0x3a0
    fops_vcodec_release+0xb7/0x190

Fix this by calling cancel_work_sync(&ctx->encode_work) before kfree(ctx).
This ensures the workqueue handler is both cancelled (if pending) and
synchronized (waits for any running handler to complete) before the
context is freed.

Placement rationale: The fix is placed after v4l2_ctrl_handler_free()
and before list_del_init(&ctx->list). At this point, all m2m operations
are done (v4l2_m2m_ctx_release() has returned), and we need to ensure
the workqueue is synchronized before removing ctx from the list and
freeing it.

Note: The open error path does NOT need cancel_work_sync() because
INIT_WORK() only initializes the work structure - it does not schedule
it. Work is only scheduled later during device_run() operations.

## References
- https://git.kernel.org/stable/c/76e35091ffc722ba39b303e48bc5d08abb59dd56
- https://git.kernel.org/stable/c/93d9a58961a9e09306857e999b3ee76aa4be67f0
- https://git.kernel.org/stable/c/9a9bdaf9dc42ccca50e53f82165292f74a365c11
- https://git.kernel.org/stable/c/a8a55913552aed45108525d1851c65e1db0cc25b
- https://git.kernel.org/stable/c/f1692337c6fa26e04f89b22a4d84bf5b7ada50d1
- https://git.kernel.org/stable/c/f99353cd0e9f58bf17889049137b8d65fb44ebf1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31584.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31584
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
