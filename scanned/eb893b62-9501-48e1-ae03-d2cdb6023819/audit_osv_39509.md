# [H] media: mtk-jpeg: fix use-after-free in release path due to uncancelled work

## Summary
Severity: High
Advisory: CVE-2026-46011
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46011
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.140, >=6.7.0 <6.12.86, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: mtk-jpeg: fix use-after-free in release path due to uncancelled work

The mtk_jpeg_release() function frees the context structure (ctx) without
first cancelling any pending or running work in ctx->jpeg_work. This
creates a race window where the workqueue callback may still be accessing
the context memory after it has been freed.

Race condition:

    CPU 0 (release)                    CPU 1 (workqueue)
    ----------------                   ------------------
    close()
      mtk_jpeg_release()
                                       mtk_jpegenc_worker()
                                         ctx = work->data
                                         // accessing ctx

        kfree(ctx)  // freed!
                                         access ctx  // UAF!

The work is queued via queue_work() during JPEG encode/decode operations
(via mtk_jpeg_device_run). If the device is closed while work is pending
or running, the work handler will access freed memory.

Fix this by calling cancel_work_sync() BEFORE acquiring the mutex. This
ordering is critical: if cancel_work_sync() is called after mutex_lock(),
and the work handler also tries to acquire the same mutex, it would cause
a deadlock.

Note: The open error path does NOT need cancel_work_sync() because
INIT_WORK() only initializes the work structure - it does not schedule
it. Work is only scheduled later during ioctl operations.

## References
- https://git.kernel.org/stable/c/0498b27a1542021d90269d58347501d4c3ccd84e
- https://git.kernel.org/stable/c/2209fdae5c2f615930c9af1379c1cfca199ec5d8
- https://git.kernel.org/stable/c/26506a30e0e26d612f82a7bf0e395626968a44e6
- https://git.kernel.org/stable/c/34c519feef3e4fcff1078dc8bdb25fbbbd10303f
- https://git.kernel.org/stable/c/e78c39f720679fcf3a2eacd82725ec3ea2648301
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46011.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46011
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
