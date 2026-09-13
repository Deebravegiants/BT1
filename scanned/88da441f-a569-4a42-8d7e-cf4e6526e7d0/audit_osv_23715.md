# [H] blk-mq: don't touch ->tagset in blk_mq_get_sq_hctx

## Summary
Severity: High
Advisory: CVE-2022-49377
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49377
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

blk-mq: don't touch ->tagset in blk_mq_get_sq_hctx

blk_mq_run_hw_queues() could be run when there isn't queued request and
after queue is cleaned up, at that time tagset is freed, because tagset
lifetime is covered by driver, and often freed after blk_cleanup_queue()
returns.

So don't touch ->tagset for figuring out current default hctx by the mapping
built in request queue, so use-after-free on tagset can be avoided. Meantime
this way should be fast than retrieving mapping from tagset.

## References
- https://git.kernel.org/stable/c/460aa288c5cd0544dcf933a2f0ad0e8c6d2d35ff
- https://git.kernel.org/stable/c/5d05426e2d5fd7df8afc866b78c36b37b00188b7
- https://git.kernel.org/stable/c/70fdd922c7bf8949f8df109cf2635dff64c90392
- https://git.kernel.org/stable/c/b140bac470b4f707cda59c7266214246238661df
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49377.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49377
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
