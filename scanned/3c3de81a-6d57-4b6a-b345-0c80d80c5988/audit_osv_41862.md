# [H] accel/rocket: fix UAF via dangling GEM handle in create_bo

## Summary
Severity: High
Advisory: CVE-2026-64008
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64008
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/rocket: fix UAF via dangling GEM handle in create_bo

rocket_ioctl_create_bo() inserts a GEM handle into the file's IDR via
drm_gem_handle_create() early on, then performs several operations that
can fail (sgt allocation, drm_mm insert, iommu_map). If any fail after
the handle is live, the error path calls drm_gem_shmem_object_free()
which kfree's the object without removing the handle from the IDR.

This leaves a dangling handle pointing to freed slab memory. Any
subsequent ioctl using that handle (PREP_BO, FINI_BO, SUBMIT) calls
drm_gem_object_lookup() and dereferences freed memory (UAF).

Fix by moving drm_gem_handle_create() to after all fallible operations
succeed, matching the pattern used by panfrost, lima, and etnaviv.

Also fix drm_mm_insert_node_generic() whose return value was silently
overwritten by iommu_map_sgtable() on the next line. Add the missing
error check.

[tomeu: Move handle creation to the very end]

## References
- https://git.kernel.org/stable/c/18abd88d19ea195e2e1547fca0970c2f91d77a42
- https://git.kernel.org/stable/c/451f1ccbbdb7b65021646704b15902655f8d228a
- https://git.kernel.org/stable/c/f706e6a4ce75585af979aec3dcbdce68bc76306b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64008.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64008
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
