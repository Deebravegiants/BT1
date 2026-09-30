# [H] zram: fix use-after-free in zram_writeback_endio

## Summary
Severity: High
Advisory: CVE-2026-63951
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63951
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

zram: fix use-after-free in zram_writeback_endio

A crash was observed in zram_writeback_endio due to a NULL pointer
dereference in wake_up.  The root cause is a race condition between the
bio completion handler (zram_writeback_endio) and the writeback task.

In zram_writeback_endio, wake_up() is called on &wb_ctl->done_wait after
releasing wb_ctl->done_lock.  This creates a race window where the
writeback task can see num_inflight become 0, return, and free wb_ctl
before zram_writeback_endio calls wake_up().

CPU 0 (zram_writeback_endio)     CPU 1 (writeback_store)
============================     ============================
                                 zram_writeback_slots
                                   zram_submit_wb_request
                                   zram_submit_wb_request
                                   wait_event(wb_ctl->done_wait)
spin_lock(&wb_ctl->done_lock);
list_add(&req->entry, &wb_ctl->done_reqs);
spin_unlock(&wb_ctl->done_lock);
wake_up(&wb_ctl->done_wait);
                                   zram_complete_done_reqs
spin_lock(&wb_ctl->done_lock);
list_add(&req->entry, &wb_ctl->done_reqs);
spin_unlock(&wb_ctl->done_lock);
                                   while (num_inflight) > 0)
                                     spin_lock(&wb_ctl->done_lock);
                                     list_del(&req->entry);
                                     spin_unlock(&wb_ctl->done_lock);
                                     // num_inflight becomes 0
                                     atomic_dec(num_inflight);

                                 // Leave zram_writeback_slots
                                 // Free wb_ctl
                                 release_wb_ctl(wb_ctl);
// UAF crash!
wake_up(&wb_ctl->done_wait);

This patch fixes this race by using RCU.  By protecting wb_ctl with
rcu_read_lock() in zram_writeback_endio and using kfree_rcu() to free it,
we ensure that wb_ctl remains valid during the execution of
zram_writeback_endio.

## References
- https://git.kernel.org/stable/c/bf62f69574b19720ae5fbbbcdf24a0c4e3e05e43
- https://git.kernel.org/stable/c/ebe2cbefc86291fa7f386447a81995640df4e2fd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63951.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63951
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
