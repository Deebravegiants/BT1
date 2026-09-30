# [H] drm/xe/vf: Fix VF CCS attach/detach race with in-flight BO moves

## Summary
Severity: High
Advisory: CVE-2026-68384
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68384
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/vf: Fix VF CCS attach/detach race with in-flight BO moves

xe_bo_move() attaches VF CCS read/write batch buffers (BBs) to a BO
after it transitions NULL/SYSTEM -> TT, and detaches them after it
transitions TT -> SYSTEM. Both operations were done synchronously on
the CPU immediately after building the move's copy/clear fence,
without waiting for that fence to signal. This creates two races with
VF migration:

- Attach happens too late relative to the copy job it is meant to
  protect. If the copy job is submitted before the CCS BBs are
  attached, a VF migration event that pauses execution mid-copy can
  observe partially copied CCS metadata without the attach state
  needed to correctly save/restore it.

- Detach happens too early relative to the copy job that moves data
  out of TT. The CCS BBs are torn down right after the copy fence is
  obtained, while the actual blit may still be in flight. A VF
  migration event that pauses execution mid-copy can then race the
  save/restore path against the still-running blit, and the CCS BBs
  it would need to make sense of the paused state have already been
  removed.

Fix both races:

- Move the attach call to before the copy/clear job is submitted, so
  the CCS BBs are already registered by the time the copy runs. On
  attach failure, unwind and bail out of the move. xe_migrate_ccs_rw_copy()
  now takes the destination resource explicitly, since bo->ttm.resource
  is not updated to the new resource until after the move commits.

- Detach only after explicitly waiting for the copy fence to signal,
  instead of tearing down the CCS BBs immediately after obtaining it.

While here, also fix xe_sriov_vf_ccs_attach_bo() to properly unwind and
propagate errors: the per-context loop previously never broke out on
error, silently discarding earlier failures. Unwind by clearing each
attached context directly via xe_migrate_ccs_rw_copy_clear() instead of
reusing xe_sriov_vf_ccs_detach_bo(), which requires both contexts to be
attached before it will clean up either one.

(cherry picked from commit d45ad0aa7a1eb5d7288b5ed948b05695611dc39e)

## References
- https://git.kernel.org/stable/c/35ba43b541117bfb595e4b807ba447cf4335cc7d
- https://git.kernel.org/stable/c/56441f9e08ad68697295b8835266d2bc48ab59b5
- https://git.kernel.org/stable/c/f2ebfd5cc87f1393a30c8b8b0a6c20cb22cffa97
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68384.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68384
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
