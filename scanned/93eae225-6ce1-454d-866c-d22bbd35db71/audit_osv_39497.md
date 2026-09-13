# [H] drm/exynos: vidi: fix to avoid directly dereferencing user pointer

## Summary
Severity: High
Advisory: CVE-2026-45958
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45958
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.4.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.77, >=6.13.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/exynos: vidi: fix to avoid directly dereferencing user pointer

In vidi_connection_ioctl(), vidi->edid(user pointer) is directly
dereferenced in the kernel.

This allows arbitrary kernel memory access from the user space, so instead
of directly accessing the user pointer in the kernel, we should modify it
to copy edid to kernel memory using copy_from_user() and use it.

## References
- https://git.kernel.org/stable/c/13537f7f6d28a87ee2e496e071b6ad9541905f23
- https://git.kernel.org/stable/c/235d702b771416b8a61e81bb09ba39282e4268fd
- https://git.kernel.org/stable/c/2e147aa3169b83eaf044776f81d86235bf147de1
- https://git.kernel.org/stable/c/4949e32387fe315b59ad5f422c9fc52836fbdd1e
- https://git.kernel.org/stable/c/4c4193829109f38b2855de77981adc2e066286c7
- https://git.kernel.org/stable/c/7efb6a4e6b1b523e744d17e6249757ed97caae7c
- https://git.kernel.org/stable/c/c2914c0ca7557c6c5c845621cb6d6c9f26ab5a8c
- https://git.kernel.org/stable/c/d4c98c077c7fb2dfdece7d605e694b5ea2665085
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45958.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45958
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
