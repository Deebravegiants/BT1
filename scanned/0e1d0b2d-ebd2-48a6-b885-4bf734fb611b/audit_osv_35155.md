# [H] accel/ivpu: Fix page fault in ivpu_bo_unbind_all_bos_from_context()

## Summary
Severity: High
Advisory: CVE-2025-68730
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2025-68730
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.17.13, >=6.18.0 <6.18.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/ivpu: Fix page fault in ivpu_bo_unbind_all_bos_from_context()

Don't add BO to the vdev->bo_list in ivpu_gem_create_object().
When failure happens inside drm_gem_shmem_create(), the BO is not
fully created and ivpu_gem_bo_free() callback will not be called
causing a deleted BO to be left on the list.

## References
- https://git.kernel.org/stable/c/8172838a284c27190fa6782c2740a97020434750
- https://git.kernel.org/stable/c/8b694b405a84696f1d964f6da7cf9721e68c4714
- https://git.kernel.org/stable/c/c9ef5ccd8bd9bcf598b6d3f77e7eb4dde7149aec
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68730.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68730
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
