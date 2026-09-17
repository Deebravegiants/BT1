# [H] mm: slub: fix flush_cpu_slab()/__free_slab() invocations in task context.

## Summary
Severity: High
Advisory: CVE-2022-48658
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-28
Source: https://osv.dev/vulnerability/CVE-2022-48658
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.71, >=5.16.0 <5.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: slub: fix flush_cpu_slab()/__free_slab() invocations in task context.

Commit 5a836bf6b09f ("mm: slub: move flush_cpu_slab() invocations
__free_slab() invocations out of IRQ context") moved all flush_cpu_slab()
invocations to the global workqueue to avoid a problem related
with deactivate_slab()/__free_slab() being called from an IRQ context
on PREEMPT_RT kernels.

When the flush_all_cpu_locked() function is called from a task context
it may happen that a workqueue with WQ_MEM_RECLAIM bit set ends up
flushing the global workqueue, this will cause a dependency issue.

 workqueue: WQ_MEM_RECLAIM nvme-delete-wq:nvme_delete_ctrl_work [nvme_core]
   is flushing !WQ_MEM_RECLAIM events:flush_cpu_slab
 WARNING: CPU: 37 PID: 410 at kernel/workqueue.c:2637
   check_flush_dependency+0x10a/0x120
 Workqueue: nvme-delete-wq nvme_delete_ctrl_work [nvme_core]
 RIP: 0010:check_flush_dependency+0x10a/0x120[  453.262125] Call Trace:
 __flush_work.isra.0+0xbf/0x220
 ? __queue_work+0x1dc/0x420
 flush_all_cpus_locked+0xfb/0x120
 __kmem_cache_shutdown+0x2b/0x320
 kmem_cache_destroy+0x49/0x100
 bioset_exit+0x143/0x190
 blk_release_queue+0xb9/0x100
 kobject_cleanup+0x37/0x130
 nvme_fc_ctrl_free+0xc6/0x150 [nvme_fc]
 nvme_free_ctrl+0x1ac/0x2b0 [nvme_core]

Fix this bug by creating a workqueue for the flush operation with
the WQ_MEM_RECLAIM bit set.

## References
- https://git.kernel.org/stable/c/61703b248be993eb4997b00ae5d3318e6d8f3c5b
- https://git.kernel.org/stable/c/df6cb39335cf5a1b918e8dbd8ba7cd9f1d00e45a
- https://git.kernel.org/stable/c/e45cc288724f0cfd497bb5920bcfa60caa335729
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48658.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48658
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
