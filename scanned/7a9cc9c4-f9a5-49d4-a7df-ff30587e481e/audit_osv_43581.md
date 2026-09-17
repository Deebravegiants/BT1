# [H] drm/radeon: fix integer overflow in radeon_align_pitch()

## Summary
Severity: High
Advisory: CVE-2026-74417
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74417
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.39 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/radeon: fix integer overflow in radeon_align_pitch()

radeon_align_pitch() has the same kind of overflow issue as the old
amdgpu helper: both the alignment round-up add and the final
'aligned * cpp' calculation can overflow signed int.

If that wraps, radeon_mode_dumb_create() can end up returning an
invalid pitch or creating a zero-sized dumb buffer.

Fix this by using check_add_overflow() for the alignment round-up and
check_mul_overflow() for the final pitch calculation, returning 0 on
overflow. Also reject zero pitch and size in
radeon_mode_dumb_create().

Found via AST-based call-graph analysis using sqry.

## References
- https://git.kernel.org/stable/c/415bb9893e249e46aa5159f7363a11512cf06fa9
- https://git.kernel.org/stable/c/b7b44937c548c2c987fcdd129f8896741004bed6
- https://git.kernel.org/stable/c/ce3b24eb3ee8f82de851535f516bf21f83e82259
- https://git.kernel.org/stable/c/d9dfa176899d488e48bb7342d2c43ddd36e66318
- https://git.kernel.org/stable/c/dfc7b5b5599472277e71e5bd2712740651c7c5be
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74417.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74417
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
