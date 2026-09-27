# [M] drm/amdgpu/gfx9: Add Cleaner Shader Deinitialization in gfx_v9_0 Module

## Summary
Severity: Medium
Advisory: CVE-2024-56753
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2024-56753
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu/gfx9: Add Cleaner Shader Deinitialization in gfx_v9_0 Module

This commit addresses an omission in the previous patch related to the
cleaner shader support for GFX9 hardware. Specifically, it adds the
necessary deinitialization code for the cleaner shader in the
gfx_v9_0_sw_fini function.

The added line amdgpu_gfx_cleaner_shader_sw_fini(adev); ensures that any
allocated resources for the cleaner shader are freed correctly, avoiding
potential memory leaks and ensuring that the GPU state is clean for the
next initialization sequence.

## References
- https://git.kernel.org/stable/c/720c0376b3d29cbab921a60062fda5980742ed9d
- https://git.kernel.org/stable/c/e47cb9d2533200d49dd5364d4a148119492f8a3d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56753.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56753
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
