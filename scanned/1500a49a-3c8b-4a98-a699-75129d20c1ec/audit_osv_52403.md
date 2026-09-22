# [M] CVE-2021-47412

## Summary
Severity: Medium
Advisory: CVE-2021-47412
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47412
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

block: don't call rq_qos_ops->done_bio if the bio isn't tracked

rq_qos framework is only applied on request based driver, so:

1) rq_qos_done_bio() needn't to be called for bio based driver

2) rq_qos_done_bio() needn't to be called for bio which isn't tracked,
such as bios ended from error handling code.

Especially in bio_endio():

1) request queue is referred via bio->bi_bdev->bd_disk->queue, which
may be gone since request queue refcount may not be held in above two
cases

2) q->rq_qos may be freed in blk_cleanup_queue() when calling into
__rq_qos_done_bio()

Fix the potential kernel panic by not calling rq_qos_ops->done_bio if
the bio isn't tracked. This way is safe because both ioc_rqos_done_bio()
and blkcg_iolatency_done_bio() are nop if the bio isn't tracked.

## References
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://git.kernel.org/stable/c/db60edbfff332a6a5477c367af8125f034570989
- https://git.kernel.org/stable/c/004b8f8a691205a93d9e80d98b786b2b97424d6e
- https://git.kernel.org/stable/c/a647a524a46736786c95cdb553a070322ca096e3
