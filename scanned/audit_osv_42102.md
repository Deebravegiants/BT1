# [H] drm/hyperv: validate resolution_count and fix WIN8 fallback

## Summary
Severity: High
Advisory: CVE-2026-64524
Ecosystem: Linux
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64524
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/hyperv: validate resolution_count and fix WIN8 fallback

A SYNTHVID_RESOLUTION_RESPONSE with resolution_count > 64 walks past
the supported_resolution[SYNTHVID_MAX_RESOLUTION_COUNT] array in the
parse loop. Bound resolution_count against the array size, folded
into the existing zero-check.

When the WIN10 resolution probe fails, the caller in
hyperv_connect_vsp() left hv->screen_*_max / preferred_* unpopulated,
which sets mode_config.max_width / max_height to 0 and makes
drm_internal_framebuffer_create() reject every userspace framebuffer
with -EINVAL. The pre-WIN10 branch had the same gap for
preferred_width / preferred_height. Use a single post-probe fallback
guarded by screen_width_max == 0 so both paths converge on the WIN8
defaults.

## References
- https://git.kernel.org/stable/c/13d33b9ef67066c77c84273fac5a1d3fde3533d1
- https://git.kernel.org/stable/c/1fb565b77b8f44afabb02de6310065f109d89e94
- https://git.kernel.org/stable/c/8a114b25b5521eae451b13bce98ae978624962e5
- https://git.kernel.org/stable/c/96f7de3172d4aa878b7f87173b2b3507c350fcd6
- https://git.kernel.org/stable/c/9c698b2c43c2667c34f5336bf46ad5786216ac2a
- https://git.kernel.org/stable/c/a321c908f2eeea01539668eb270d074d9b88e490
- https://git.kernel.org/stable/c/bc573752f3dac0d1ab8df7078c1851bc76717653
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64524.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64524
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
