# [H] drm/xe: Hold a dma-buf reference for imported BOs

## Summary
Severity: High
Advisory: CVE-2026-68266
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68266
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.103, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe: Hold a dma-buf reference for imported BOs

An imported dma-buf BO is created as a ttm_bo_type_sg BO whose
reservation object is the exporter's dma_buf->resv. The importer,
however, only takes a dma-buf reference after a successful
dma_buf_dynamic_attach(). Until then nothing keeps the exporter alive,
so if the exporter is freed while the BO still references its resv, a
later access to that resv is a use-after-free:

  Oops: general protection fault, probably for non-canonical address
        0x6b6b6b6b6b6b6b9c
  Workqueue: ttm ttm_bo_delayed_delete [ttm]
  RIP: 0010:mutex_can_spin_on_owner+0x3f/0xc0

This can be reached on two paths:

 - dma_buf_dynamic_attach() fails, or
 - ttm_bo_init_reserved() fails during BO creation.

In both cases the BO already has bo->base.resv pointing at the exporter
resv, and sg BOs are always torn down via ttm_bo_delayed_delete(), which
locks bo->base.resv asynchronously - potentially after the exporter has
been freed.

Take the dma-buf reference in xe_bo_init_locked(), before
ttm_bo_init_reserved(), so it also covers a creation failure there, and
release it in xe_ttm_bo_destroy(). The reference is held for the whole
BO lifetime, keeping the shared resv alive on every path.

v2:
  - Reworked the fix to avoid creating the imported sg BO before
    dma_buf_dynamic_attach() succeeds.
  - Attach with importer_priv == NULL and make invalidate_mappings ignore
    incomplete imports.

v3:
  - Dropped the xe-side reordering approach since importer_priv must be
    valid when dma_buf_dynamic_attach() publishes the attachment.
  - Per Christian's suggestion on the v1 thread, keyed the check on
    import_attach rather than removing the sg guard entirely.
  - Fixes both xe and amdgpu in a single TTM patch.

v4:
  - Moved import_attach check to after dma_resv_copy_fences() so fences
    are copied before returning for successful imports (Thomas).
  - Removed exporter-alive claim from commit message (Thomas).

v5:
  - Add drm/xe patch to keep imported sg BOs off the LRU before attach
    succeeds; the TTM fix alone is not sufficient for xe if the BO is
    already LRU-visible. (Thomas)
    v4 patch:
    https://patchwork.freedesktop.org/patch/736663/?series=169129&rev=2
  - Patch 1 (drm/ttm) carries Christian's Reviewed-by from v4.

v6:
  - Reworked the fix based on Thomas' suggestion. Instead of the TTM resv
    individualization (v1-v5) plus the xe off-LRU/placement handling (v5),
    just hold a dma-buf reference for the imported BO lifetime so the
    shared resv can never be freed while the BO still references it.
    Single xe patch, no TTM change. (Thomas)
  - Take the reference in xe_bo_init_locked() before ttm_bo_init_reserved()
    so a TTM creation failure is covered too (Thomas).
  - Dropped the v5 series (drm/ttm + drm/xe off-LRU); the off-LRU approach
    also regressed in CI BAT via ttm_bo_pipeline_gutting() creating a ghost
    BO that outlived the exporter.
    Link to v5: https://patchwork.freedesktop.org/series/169984/

v7:
  - Move changelog above --- so it stays in the commit message.
  - Reorder changelog entries oldest-to-newest. (Thomas)

(cherry picked from commit 3516f3fae6be35642f8f06f8a218da6425c0306a)

## References
- https://git.kernel.org/stable/c/62775525a27c3b0d56382e08ba81ee2d322058b6
- https://git.kernel.org/stable/c/ba8c4cbb31c6f81fa5b12d6e28f1f706040aff48
- https://git.kernel.org/stable/c/c1954c66662de477a8f4309335b775f7b07bd28b
- https://git.kernel.org/stable/c/c22d65d62b3318e237c0e5b1177d90ab83d9fe06
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68266.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68266
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
