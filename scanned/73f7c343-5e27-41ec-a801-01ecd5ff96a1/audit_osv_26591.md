# [H] drm/i915/dpt: Treat the DPT BO as a framebuffer

## Summary
Severity: High
Advisory: CVE-2023-53378
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53378
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.23, >=6.2.0 <6.2.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/i915/dpt: Treat the DPT BO as a framebuffer

Currently i915_gem_object_is_framebuffer() doesn't treat the
BO containing the framebuffer's DPT as a framebuffer itself.
This means eg. that the shrinker can evict the DPT BO while
leaving the actual FB BO bound, when the DPT is allocated
from regular shmem.

That causes an immediate oops during hibernate as we
try to rewrite the PTEs inside the already evicted
DPT obj.

TODO: presumably this might also be the reason for the
DPT related display faults under heavy memory pressure,
but I'm still not sure how that would happen as the object
should be pinned by intel_dpt_pin() while in active use by
the display engine...

(cherry picked from commit 779cb5ba64ec7df80675a956c9022929514f517a)

## References
- https://git.kernel.org/stable/c/3413881e1ecc3cba722a2e87ec099692eed5be28
- https://git.kernel.org/stable/c/5390a02b4508416b9bee96674f141c68f89bafbc
- https://git.kernel.org/stable/c/c781c107731fc09ce4330c8c636b8446d0f72aa4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53378.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53378
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
