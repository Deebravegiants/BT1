# [M] iommu/arm-smmu-v3: check return value after calling platform_get_resource()

## Summary
Severity: Medium
Advisory: CVE-2022-49319
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49319
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/arm-smmu-v3: check return value after calling platform_get_resource()

It will cause null-ptr-deref if platform_get_resource() returns NULL,
we need check the return value.

## References
- https://git.kernel.org/stable/c/54c1e0e3bbcab2abe25b2874a43050ae5df87831
- https://git.kernel.org/stable/c/54cf47da0c7532d151d76e5d63f5936191698c44
- https://git.kernel.org/stable/c/b131fa8c1d2afd05d0b7598621114674289c2fbb
- https://git.kernel.org/stable/c/db728a891f9177b044aaca89b678f6b5e24d5cc3
- https://git.kernel.org/stable/c/fb0f1c5eb8d60b3e018ba7c87da249b52674ebe6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49319.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49319
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
