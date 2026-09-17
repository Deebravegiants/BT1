# [H] drm/amdgpu: invoke pm_genpd_remove() before freeing genpd

## Summary
Severity: High
Advisory: CVE-2026-68104
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68104
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: invoke pm_genpd_remove() before freeing genpd

Call pm_genpd_remove() to unregister from global list prior to releasing
acp_genpd memory, and clear the pointer after free.

(cherry picked from commit cd8650d7a91ee8b768e202354672553faa5cc1f2)

## References
- https://git.kernel.org/stable/c/08fee493e0261f9e4120a5c8e7e42e8a723574e8
- https://git.kernel.org/stable/c/28c9b3c5dc35cc790d11e26ca3fc6e068be63998
- https://git.kernel.org/stable/c/2e406b86144c1f732eb344f1f1e09043856cfc33
- https://git.kernel.org/stable/c/493adf29d66f23888f0e29888b6bc9512acd0825
- https://git.kernel.org/stable/c/4d7c10b0bf09d90c81818752decbdb1966b62702
- https://git.kernel.org/stable/c/5c0a82283271759fff445ac27182072f200a888c
- https://git.kernel.org/stable/c/930a5dc3df4aa5e10393134bd5313d616dbebaf6
- https://git.kernel.org/stable/c/bdfc7f1e0900ef1361b828c4f69b72701f8a0a86
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68104.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68104
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
