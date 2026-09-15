# [H] drm/xe/vm: Fix BO prefetch with CONSULT_MEM_ADVISE_PREF_LOC

## Summary
Severity: High
Advisory: CVE-2026-68265
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68265
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.44, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/vm: Fix BO prefetch with CONSULT_MEM_ADVISE_PREF_LOC

When prefetch region is DRM_XE_CONSULT_MEM_ADVISE_PREF_LOC for a BO VMA,
the code used it as an index into region_to_mem_type[], causing an
out-of-bounds access since the value is -1.

Resolve the preferred location for BO VMAs directly: local VRAM on dGFX
(using the BO's tile placement) or system memory on iGPU.

Discovered using AI-assisted static analysis confirmed by Intel Product
Security.

v2:
-Fix null dereference

(cherry picked from commit d9a4906ac03be9f6ed3f3b45c56c866b867fd75b)

## References
- https://git.kernel.org/stable/c/7bc597ce74bab4153b2009c92eccf889e9d74044
- https://git.kernel.org/stable/c/c4affa4e8bc8086b4d3e8d6cf1055a624f813d72
- https://git.kernel.org/stable/c/d256dac008d1d9e6378aa1a5454e89a8292d174c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68265.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68265
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
