# [M] drm/rockchip: vop: fix possible null-ptr-deref in vop_bind()

## Summary
Severity: Medium
Advisory: CVE-2022-49491
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49491
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/rockchip: vop: fix possible null-ptr-deref in vop_bind()

It will cause null-ptr-deref in resource_size(), if platform_get_resource()
returns NULL, move calling resource_size() after devm_ioremap_resource() that
will check 'res' to avoid null-ptr-deref.

## References
- https://git.kernel.org/stable/c/3451852312303d54a003c73bd0ae39cebb960bd5
- https://git.kernel.org/stable/c/452922955df215a417c80d09dab72bbc667a1861
- https://git.kernel.org/stable/c/6ff986e057bf28e2f7690dad410768b2270f9453
- https://git.kernel.org/stable/c/769c53bb6116d0eaec0f1fe4ec4b27a74465cad1
- https://git.kernel.org/stable/c/a9b4599665e437de8a1152799c34841b799a2e1c
- https://git.kernel.org/stable/c/b54926bd558d97c888c3d2d87886f3c159d3254a
- https://git.kernel.org/stable/c/ecfa52654d0c9c333c1fe1611f47105f6bce9591
- https://git.kernel.org/stable/c/f8c242908ad15bbd604d3bcb54961b7d454c43f8
- https://git.kernel.org/stable/c/fcd6a886443730c39170b8383411e52118aec0a3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49491.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49491
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
