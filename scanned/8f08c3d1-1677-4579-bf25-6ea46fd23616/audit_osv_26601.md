# [H] drm/mediatek: Clean dangling pointer on bind error path

## Summary
Severity: High
Advisory: CVE-2023-53388
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53388
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <4.19.276, >=4.20.0 <5.4.235, >=5.5.0 <5.10.173, >=5.11.0 <5.15.99, >=5.16.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/mediatek: Clean dangling pointer on bind error path

mtk_drm_bind() can fail, in which case drm_dev_put() is called,
destroying the drm_device object. However a pointer to it was still
being held in the private object, and that pointer would be passed along
to DRM in mtk_drm_sys_prepare() if a suspend were triggered at that
point, resulting in a panic. Clean the pointer when destroying the
object in the error path to prevent this from happening.

## References
- https://git.kernel.org/stable/c/36aa8c61af55675ed967900fbe5deb32d776f051
- https://git.kernel.org/stable/c/49cf87919daeeeeeb9e924c39bdd9203af434461
- https://git.kernel.org/stable/c/6a89ddee1686a8872384aaa9f0bcfa6b675acd86
- https://git.kernel.org/stable/c/7b551a501fa714890e55bae73efede1185728d72
- https://git.kernel.org/stable/c/9a48f99aa7bea15e0b1d8b0040c46b4792eddf3b
- https://git.kernel.org/stable/c/a161f1d92aabb3b8463f752bdc3474dc3a5ec0e5
- https://git.kernel.org/stable/c/f3887c771576c5d740c5c5b8bf654a8ab8020b7d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53388.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53388
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
