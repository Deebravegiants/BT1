# [H] drm/vmwgfx: Validate vmw_surface_metadata::array_size

## Summary
Severity: High
Advisory: CVE-2026-68446
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-68446
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/vmwgfx: Validate vmw_surface_metadata::array_size

This field comes from userspace and should be validated against specific
limits depending on which Shader Model (SM) is available.

## References
- https://git.kernel.org/stable/c/0403cec2aff8037bc246cf9a0831eb169ddcd9df
- https://git.kernel.org/stable/c/5ff94e1279176b539d451e3e754fdcbd1a8d520a
- https://git.kernel.org/stable/c/6910ccaf41678f7761ba2e57d72b77d056320b4d
- https://git.kernel.org/stable/c/71779fe8bf403a9b3e28dc59229fa556db32d35d
- https://git.kernel.org/stable/c/a4f55260f7f7d4dc4d0ee55063dfb0c457b77991
- https://git.kernel.org/stable/c/aded8463466ede7a7fbd1bbf821756c67c83e89b
- https://git.kernel.org/stable/c/b1379f0c42b88cb60b9f3757eb5d1e73ad460ed8
- https://git.kernel.org/stable/c/e949adf2d42678fb391a41db277e2fcb12090566
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68446.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68446
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
