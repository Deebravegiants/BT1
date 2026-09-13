# [H] drm/amdgpu/jpeg: set no_user_fence for JPEG v5.3.0 ring

## Summary
Severity: High
Advisory: CVE-2026-63840
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63840
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.0.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu/jpeg: set no_user_fence for JPEG v5.3.0 ring

JPEG rings do not support 64-bit user fence writes, reject CS
submissions with user fences.

(cherry picked from commit 86ac011ae234c03fb872f4945913391ea1d8862e)

## References
- https://git.kernel.org/stable/c/3b0ea2021351b6b813b34fac940957f1f4fad85b
- https://git.kernel.org/stable/c/46ad73aec27d020f103b4262e4da2d2c22f54799
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63840.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63840
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
