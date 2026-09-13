# [H] drm/i915: Fix potential bit_17 double-free

## Summary
Severity: High
Advisory: CVE-2023-52930
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-52930
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.168, >=5.11.0 <5.15.93, >=5.16.0 <6.1.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/i915: Fix potential bit_17 double-free

A userspace with multiple threads racing I915_GEM_SET_TILING to set the
tiling to I915_TILING_NONE could trigger a double free of the bit_17
bitmask.  (Or conversely leak memory on the transition to tiled.)  Move
allocation/free'ing of the bitmask within the section protected by the
obj lock.

[tursulin: Correct fixes tag and added cc stable.]
(cherry picked from commit 10e0cbaaf1104f449d695c80bcacf930dcd3c42e)

## References
- https://git.kernel.org/stable/c/0769f997a7b6d5cb8336db0b4ec3d2d311b8097c
- https://git.kernel.org/stable/c/7057a8f126f14f14b040faecfa220fd27c6c2f85
- https://git.kernel.org/stable/c/b591abac78e25269b12e3d7170c99463f8c5cb02
- https://git.kernel.org/stable/c/e3ebc3e23bd9028a8a9a26cbc5985f99be445f65
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52930.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52930
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
