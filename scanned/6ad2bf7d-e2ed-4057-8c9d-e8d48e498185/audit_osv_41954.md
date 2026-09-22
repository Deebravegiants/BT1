# [H] drm/msm: Fix iommu_map_sgtable() return value check and avoid WARN

## Summary
Severity: High
Advisory: CVE-2026-64153
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64153
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm: Fix iommu_map_sgtable() return value check and avoid WARN

Commit "iommu: return full error code from iommu_map_sg[_atomic]()"
changed iommu_map_sgtable() to return an ssize_t and negative values
in error cases, rather than a size_t and a zero.

Store the return value in the appropriate type and in case of error,
return it rather than WARNing.

Patchwork: https://patchwork.freedesktop.org/patch/719685/

## References
- https://git.kernel.org/stable/c/3457807aeb88077712f0a7cb65c3ca5120773d75
- https://git.kernel.org/stable/c/3a45af37733446e114bf19b0209fe7d8089bdb8b
- https://git.kernel.org/stable/c/3c2cdb7c07f664b77e2a75b50793b845d5742efa
- https://git.kernel.org/stable/c/3e3c3c95ef4fe17231a9149e27bcfc9dae2dd89f
- https://git.kernel.org/stable/c/55e0f0d1c1a4ee1e46da7da4d443eb3044fb3851
- https://git.kernel.org/stable/c/7256e54583aee21e23929e7554278c2f5c1a08b1
- https://git.kernel.org/stable/c/f4e37f3df436c2bdd2621c21f9c72c8f149a221d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64153.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64153
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
