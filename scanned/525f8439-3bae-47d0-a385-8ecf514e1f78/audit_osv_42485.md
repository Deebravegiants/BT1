# [H] drm/imagination: Fix user array stride in pvr_set_uobj_array()

## Summary
Severity: High
Advisory: CVE-2026-68262
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68262
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/imagination: Fix user array stride in pvr_set_uobj_array()

pvr_set_uobj_array() copies an array of kernel objects to a userspace
array whose element size is described by out->stride. When out->stride
is different from the kernel object size, the slow path advances the
userspace pointer by the kernel object size and the kernel pointer by the
userspace stride.

This reverses the intended layout. For larger userspace strides, later
copies read from the wrong kernel addresses. For smaller userspace
strides, later copies are written at the wrong userspace offsets. The
padding clear is also done only for the first element instead of the
padding area for each element.

Advance the userspace pointer by out->stride and the kernel pointer by
obj_size, and clear per-element padding while the current userspace
pointer is still available.

## References
- https://git.kernel.org/stable/c/09beaf4aec05b0525f2153dce693f3eb3166697a
- https://git.kernel.org/stable/c/8dc8f3f4c2382fb7d1b1986ba8f33a2466cd3d7a
- https://git.kernel.org/stable/c/b983a35dad3701399c692d7c6eb57d8b6ffc0929
- https://git.kernel.org/stable/c/bbebc39a70f6fc9b02637c8624349e30325873cb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68262.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68262
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
