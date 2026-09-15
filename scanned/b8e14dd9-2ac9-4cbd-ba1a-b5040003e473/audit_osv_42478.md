# [H] drm/gpusvm: publish dpagemap early to avoid device mapping leak on error

## Summary
Severity: High
Advisory: CVE-2026-68240
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68240
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.44, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/gpusvm: publish dpagemap early to avoid device mapping leak on error

drm_gpusvm_get_pages() only stored the local dpagemap into
svm_pages->dpagemap on the success path. If a later page failed (e.g.
-EOPNOTSUPP when ctx->allow_mixed is false) and jumped to err_unmap,
svm_pages->dpagemap was still NULL, so __drm_gpusvm_unmap_pages() skipped
device_unmap() and leaked the device mappings already created.

Assign svm_pages->dpagemap when the first device page is mapped so the
err_unmap path can device_unmap() those mappings.

This issue was found by Sashiko AI review.

## References
- https://git.kernel.org/stable/c/72e4fca5529e45b5beebad79d804de442f632324
- https://git.kernel.org/stable/c/7f708f51e3955bda0d77a0b67ab9bea6c97fea99
- https://git.kernel.org/stable/c/e8362523fd1b61712f7d996802f9b5dee545c7e6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68240.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68240
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
