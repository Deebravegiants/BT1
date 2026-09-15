# [H] drm/xe/guc: Hold device ref until queue teardown completes

## Summary
Severity: High
Advisory: CVE-2026-68382
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68382
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/guc: Hold device ref until queue teardown completes

GuC exec queue destruction can run asynchronously. If the final device
put happens from a destroy worker, drmm cleanup can end up draining
the same workqueue and deadlock.

Hold a drm_device reference for the queue lifetime and drop it after
queue teardown completes. This keeps drmm cleanup from running while
async destroy work is still pending.

Move GuC destroy work to a module-lifetime Xe workqueue and flush it
on PCI remove so hot-unbind/rebind still waits for pending destroy work.

With queue-held device refs, guc_submit_sw_fini() cannot run with live
GuC IDs. Replace the fini wait with an assertion and remove the unused
fini_wq.

v2:
  - Rebase

v3:
  - Switch to queue-lifetime drm_dev_get()/drm_dev_put() model. (Matt)
  - Queue async teardown on system_dfl_wq instead of xe->destroy_wq. (Matt)
  - Drop separate deferred drm_dev_put worker.
  - Remove stale drain_workqueue(xe->destroy_wq) from guc_submit_sw_fini().

v4:
  - Replace the guc_submit_sw_fini() wait with an assertion and remove
    the now-unused fini_wq. (sashiko)

v5:
  - Move destroy work to a module-lifetime Xe workqueue instead of
    system_dfl_wq. (Matt)
  - Flush the module-lifetime destroy workqueue during PCI remove to
    preserve the old device-remove wait semantics.

v6:
  - Keep SVM pagemap destroy work on the per-device destroy_wq to avoid
    letting it outlive the xe_device/drm_device. (Sashiko)
  - Use WQ_MEM_RECLAIM for xe->destroy_wq because SVM pagemap destroy work
    can be queued from the reclaim path.

v7:
  - Drop the per-device xe->destroy_wq and use the module-level destroy WQ
    for SVM pagemap destroy as well. (Matt)
  - Rename xe_exec_queue_destroy_wq_*() helpers to xe_destroy_wq_*()
    helpers because the WQ is no longer exec-queue specific. (Matt)

v8:
  - Rebase.

v9:
  - Keep SVM pagemap destroy work on the per-device WQ_MEM_RECLAIM
    destroy_wq because it can be queued from reclaim and embeds
    the dev_pagemap used by devres teardown. (Sashiko)
  - Keep the module-level destroy WQ GuC-only and drop WQ_MEM_RECLAIM
    from it.
  - Update the module-WQ kdoc to document the GuC/SVM split.

v10:
  - Keep xe->destroy_wq per-cpu while adding WQ_MEM_RECLAIM to fix the
    workqueue allocation warning.

v11:
  - Drop the SVM pagemap destroy comment as it was revision-specific.
    (Thomas)

v12:
  - Rebase.

(cherry picked from commit da1124abac689cc2b1d8995e5f0a816f8a122edb)

## References
- https://git.kernel.org/stable/c/03d6f83979b0d75a0b0893dfe1735ec93facf515
- https://git.kernel.org/stable/c/9b7e60184f4b22e893d4ae95234d5f26261a430c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68382.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68382
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
