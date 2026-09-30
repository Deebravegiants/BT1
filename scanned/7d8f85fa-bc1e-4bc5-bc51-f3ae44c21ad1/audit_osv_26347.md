# [H] drm/i915: Fix potential context UAFs

## Summary
Severity: High
Advisory: CVE-2023-52913
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-21
Source: https://osv.dev/vulnerability/CVE-2023-52913
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.15.171, >=5.16.0 <6.1.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/i915: Fix potential context UAFs

gem_context_register() makes the context visible to userspace, and which
point a separate thread can trigger the I915_GEM_CONTEXT_DESTROY ioctl.
So we need to ensure that nothing uses the ctx ptr after this.  And we
need to ensure that adding the ctx to the xarray is the *last* thing
that gem_context_register() does with the ctx pointer.

[tursulin: Stable and fixes tags add/tidy.]
(cherry picked from commit bed4b455cf5374e68879be56971c1da563bcd90c)

## References
- https://git.kernel.org/stable/c/ae278887193110dfeb857ea63e243a3851fbb0bc
- https://git.kernel.org/stable/c/afce71ff6daa9c0f852df0727fe32c6fb107f0fa
- https://git.kernel.org/stable/c/b696c627b3f56e173f7f70b8487d66da8ff22506
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52913.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52913
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
