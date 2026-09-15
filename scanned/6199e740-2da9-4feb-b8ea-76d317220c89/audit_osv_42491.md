# [H] drm/xe/guc: Fix buffer overflow in steered register list allocation

## Summary
Severity: High
Advisory: CVE-2026-68274
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68274
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.18.44, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/guc: Fix buffer overflow in steered register list allocation

The size calculation for the steered register extarray uses only the
geometry DSS mask (g_dss_mask) to determine the number of entries to
allocate:

  total = bitmap_weight(gt->fuse_topo.g_dss_mask, ...) * steer_reg_num;

However, the filling loop uses for_each_dss_steering(), which iterates
over for_each_dss(), defined as the union of g_dss_mask and c_dss_mask
(geometry + compute DSS). On platforms with compute-only DSS bits, the
loop writes past the allocated buffer, corrupting adjacent slab objects.

This manifests as list_del corruption and SLUB redzone overwrites during
drm_managed_release on device unbind, since the overflow corrupts the
drmres list_head of neighboring allocations.

Fix by computing the allocation size using the union of both DSS masks,
matching the iteration pattern of for_each_dss_steering().

--
v2:
- use bitmap_weighted_or() (Zhanjun)

(cherry picked from commit 0a78a44f4901aa6c9263e66be7fce02282f1109f)

## References
- https://git.kernel.org/stable/c/632ecc90e1ca5d3b6822bb4d08f84a175b6c42c0
- https://git.kernel.org/stable/c/a9a020f3c11eba6573b699f9cf9245a51b025ade
- https://git.kernel.org/stable/c/b485bfb45555163bfa5f565d6a3415fcb3035b02
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68274.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68274
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
