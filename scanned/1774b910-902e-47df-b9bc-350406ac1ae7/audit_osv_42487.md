# [H] drm/xe/pt: Reset current_op in xe_pt_update_ops_init()

## Summary
Severity: High
Advisory: CVE-2026-68264
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68264
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/pt: Reset current_op in xe_pt_update_ops_init()

xe_pt_update_ops_init() fails to reset current_op to 0. On the
vm_bind path, ops_execute() calls xe_pt_update_ops_prepare() inside
the xe_validation_guard() / drm_exec_until_all_locked() loop. When
that loop retries due to lock contention or OOM eviction
(drm_exec_retry_on_contention() / xe_validation_retry_on_oom()),
xe_pt_update_ops_prepare() runs again on the same vops, and each
call to bind_op_prepare() increments current_op without resetting it.

After N retries current_op exceeds the array size allocated by
xe_vma_ops_alloc(), causing an out-of-bounds write into
SLUB-poisoned memory and a subsequent UAF crash in
xe_migrate_update_pgtables_cpu() when reading the corrupted pt_op->bind.

Also reset needs_svm_lock and needs_invalidation which are derived in
the same prepare pass and would otherwise cause wrong migrate ops
selection and redundant TLB invalidation on retry.

Fix this by resetting current_op, needs_svm_lock and needs_invalidation
in xe_pt_update_ops_init().

v2 (Matt):
   - Add details in commit message.
   - Add Fixes tag and Cc to stable@vger.kernel.org

(cherry picked from commit 046045543e530605c441063535e7dca0075369a6)

## References
- https://git.kernel.org/stable/c/157b1e3384d7d37f59c0c2b2ff2af8f557db1daa
- https://git.kernel.org/stable/c/6384271ac1ac0099198d15df79212a19ebdb929d
- https://git.kernel.org/stable/c/90e4fd331b980259c40118d05b89b0ec514e7c48
- https://git.kernel.org/stable/c/be5c39730ab8f1dfe59983bf7d8e3705541d1fee
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68264.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68264
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
