# [H] drm/xe/userptr: Hold notifier_lock for write on inject test path

## Summary
Severity: High
Advisory: CVE-2026-80606
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80606
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/userptr: Hold notifier_lock for write on inject test path

When CONFIG_DRM_XE_USERPTR_INVAL_INJECT=y, xe_pt_svm_userptr_pre_commit()
runs vma_check_userptr() with the svm notifier_lock taken for read. The
test injection causes vma_check_userptr() to call
xe_vma_userptr_force_invalidate(), which feeds into
xe_vma_userptr_do_inval() with drm_gpusvm_ctx.in_notifier=true. That
flag tells drm_gpusvm_unmap_pages() the caller already holds
notifier_lock for write and only asserts the mode. Because the caller
actually holds it for read, the assertion fires:

  WARNING: drivers/gpu/drm/drm_gpusvm.c:1669 at \
           drm_gpusvm_unmap_pages+0xd4/0x130 [drm_gpusvm_helper]
  Call Trace:
   xe_vma_userptr_do_inval+0x40d/0xfd0 [xe]
   xe_vma_userptr_invalidate_pass1+0x3e6/0x8d0 [xe]
   xe_vma_userptr_force_invalidate+0xde/0x290 [xe]
   vma_check_userptr.constprop.0+0x1c6/0x220 [xe]
   xe_pt_svm_userptr_pre_commit+0x6a3/0xc60 [xe]
   ...
   xe_vm_bind_ioctl+0x3a0a/0x4480 [xe]

Acquire notifier_lock for write in pre-commit when the inject Kconfig
is enabled, via new helpers xe_pt_svm_userptr_notifier_lock()/_unlock().
Rename xe_svm_assert_held_read() to
xe_svm_assert_held_read_or_inject_write() so it asserts the correct
mode under each build configuration. Production builds
(CONFIG_DRM_XE_USERPTR_INVAL_INJECT=n) keep the existing read-mode
behavior bit-for-bit.

(cherry picked from commit 80ccbd97ffee8ad2e73167d826fe7be548364365)

## References
- https://git.kernel.org/stable/c/ab9ea5c943c7e780124e75b7ffad9f1c752b2579
- https://git.kernel.org/stable/c/dca6e08c923a44d2d66b955e03dd57a3a38c2b94
- https://git.kernel.org/stable/c/f9a9abd7bbdab3dfe1b1155e1457dc02b5e14ea5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80606.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80606
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
