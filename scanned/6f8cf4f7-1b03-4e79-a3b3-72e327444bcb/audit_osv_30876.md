# [M] drm/i915: Fix NULL pointer dereference in capture_engine

## Summary
Severity: Medium
Advisory: CVE-2024-56667
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56667
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.67, >=6.7.0 <6.12.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/i915: Fix NULL pointer dereference in capture_engine

When the intel_context structure contains NULL,
it raises a NULL pointer dereference error in drm_info().

(cherry picked from commit 754302a5bc1bd8fd3b7d85c168b0a1af6d4bba4d)

## References
- https://git.kernel.org/stable/c/da0b986256ae9a78b0215214ff44f271bfe237c1
- https://git.kernel.org/stable/c/e07f9c92bd127f8835ac669d83b5e7ff59bbb40f
- https://git.kernel.org/stable/c/e6ebe4f14a267bc431d0eebab4f335c0ebd45977
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56667.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56667
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
