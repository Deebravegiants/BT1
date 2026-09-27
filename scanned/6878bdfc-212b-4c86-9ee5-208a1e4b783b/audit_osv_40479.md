# [H] drm/xe/eustall: Fix drm_dev_put called before stream disable in close

## Summary
Severity: High
Advisory: CVE-2026-53290
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-53290
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/eustall: Fix drm_dev_put called before stream disable in close

In xe_eu_stall_stream_close(), drm_dev_put() is called before the
stream is disabled and its resources are freed. If this drops the
last reference, the device structures could be freed while the
subsequent cleanup code still accesses them, leading to a
use-after-free.

Fix this by moving drm_dev_put() after all device accesses are
complete. This matches the ordering in xe_oa_release().

(cherry picked from commit 35aff528f7297e949e5e19c9cd7fd748cf1cf21c)

## References
- https://git.kernel.org/stable/c/84f2bfbe6e38f8b9815ca00826e53b7f51420402
- https://git.kernel.org/stable/c/bebce43f34b5feb8a760aa832eba81e0f8a38871
- https://git.kernel.org/stable/c/dc2d9842c67d883d3200ae33b9c3859dd9492408
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53290.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53290
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
