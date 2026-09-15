# [H] drm/imagination: Fix double call to drm_sched_entity_fini()

## Summary
Severity: High
Advisory: CVE-2026-68263
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68263
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/imagination: Fix double call to drm_sched_entity_fini()

Call sequence of double call:
pvr_context_destroy
  pvr_context_kill_queues
    pvr_queue_kill
      drm_sched_entity_destroy
        drm_sched_entity_fini // here
  pvr_context_put
    kref_put(..., pvr_context_release)
      pvr_context_destroy_queues
        pvr_queue_destroy
          drm_sched_entity_fini // here

Call to drm_sched_entity_destroy() from pvr_context_kill_queues() calls
drm_sched_entity_flush() + drm_sched_entity_fini().
drm_sched_entity_flush() ensures all pending jobs are completed and
drm_sched_entity_fini() ensures no further submission is allowed as
per expectation from pvr_context_kill_queues(). Double call to
drm_sched_entity_fini() is misuse of the API so keep call only in
pvr_context_create() failure path.

Stack trace for issue with addition of refcounting for DRM entity
stats in commit fd177135f0e6 ("drm/sched: Account entity GPU time"):

[  789.490527] ------------[ cut here ]------------
[  789.490559] refcount_t: underflow; use-after-free.
[  789.490657] WARNING: lib/refcount.c:28 at refcount_warn_saturate+0xf4/0x144, CPU#0: kworker/u16:1/440
[  789.490695] Modules linked in: powervr drm_gpuvm drm_exec gpu_sched drm_shmem_helper xhci_plat_hcd xhci_hcd dwc3 usbcore usb_common snd_soc_simple_card snd_soc_simple_card_utils sa2ul sha512 sha256 dwc3_am62 sha1 authenc rti_wdt libsha512 at24 sch_fq_codel fuse dm_mod ipv6
[  789.490798] CPU: 0 UID: 0 PID: 440 Comm: kworker/u16:1 Not tainted 7.0.0-rc7-02049-g5e2c0700091b #22 PREEMPT
[  789.490809] Hardware name: Texas Instruments AM625 SK (DT)
[  789.490815] Workqueue: powervr-sched pvr_queue_fence_release_work [powervr]
[  789.490868] pstate: 60000005 (nZCv daif -PAN -UAO -TCO -DIT -SSBS BTYPE=--)
[  789.490876] pc : refcount_warn_saturate+0xf4/0x144
[  789.490884] lr : refcount_warn_saturate+0xf4/0x144
[  789.490892] sp : ffff8000822cbcc0
[  789.490895] x29: ffff8000822cbcc0 x28: 0000000000000000 x27: 0000000000000000
[  789.490909] x26: 0000000000000000 x25: ffff800081b1e338 x24: ffff000004541405
[  789.490922] x23: ffff000004bea950 x22: ffff00000042e400 x21: ffff000007123e30
[  789.490935] x20: ffff000007123000 x19: ffff000007a80d50 x18: fffffffffffe7768
[  789.490948] x17: 74736574202c6e6f x16: 697461746e656d65 x15: ffff800081b269f0
[  789.490962] x14: 0000000000000030 x13: ffff800081b26a70 x12: 0000000000000211
[  789.490975] x11: 00000000000000c0 x10: 0000000000000b50 x9 : ffff8000822cbb30
[  789.490988] x8 : ffff0000014e7bb0 x7 : ffff00007725e780 x6 : 0000000372a05f49
[  789.491001] x5 : 0000000000000000 x4 : 0000000000000001 x3 : 0000000000000010
[  789.491013] x2 : 0000000000000000 x1 : 0000000000000000 x0 : ffff0000014e7000
[  789.491027] Call trace:
[  789.491032]  refcount_warn_saturate+0xf4/0x144 (P)
[  789.491043]  drm_sched_entity_fini+0x164/0x18c [gpu_sched]
[  789.491081]  pvr_queue_destroy+0x64/0x134 [powervr]
[  789.491110]  pvr_context_destroy_queues+0x34/0x64 [powervr]
[  789.491138]  pvr_context_release+0x70/0xac [powervr]
[  789.491166]  pvr_context_put.part.0+0x5c/0x7c [powervr]
[  789.491193]  pvr_context_put+0x14/0x24 [powervr]
[  789.491221]  pvr_queue_fence_release_work+0x20/0x38 [powervr]
[  789.491249]  process_one_work+0x160/0x4c4
[  789.491264]  worker_thread+0x188/0x310
[  789.491276]  kthread+0x130/0x13c
[  789.491287]  ret_from_fork+0x10/0x20
[  789.491300] ---[ end trace 0000000000000000 ]---

## References
- https://git.kernel.org/stable/c/4af24c27a39ba147a613a09e10b9e0f7294524c0
- https://git.kernel.org/stable/c/9be3f4bd6f514f69c51a8c77ea64fce2729dc7f4
- https://git.kernel.org/stable/c/c1136d907fd04ca5c62ba11c1159b5fe65a1760c
- https://git.kernel.org/stable/c/c88fdbf3da26e0179629530cae7768cd3d4ead85
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68263.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68263
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
