# [H] iommu/arm-smmu-v3-sva: Fix mm use-after-free

## Summary
Severity: High
Advisory: CVE-2022-49426
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49426
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/arm-smmu-v3-sva: Fix mm use-after-free

We currently call arm64_mm_context_put() without holding a reference to
the mm, which can result in use-after-free. Call mmgrab()/mmdrop() to
ensure the mm only gets freed after we unpinned the ASID.

## References
- https://git.kernel.org/stable/c/9aa215450888cf29af0c479e14a712dc6b0c506c
- https://git.kernel.org/stable/c/cbd23144f7662b00bcde32a938c4a4057e476d68
- https://git.kernel.org/stable/c/e3cbbdbff8a4db5d053c53fd71be62ccccdb52b0
- https://git.kernel.org/stable/c/fc90f13ea0dcd960e5002d204fa55cec4e0db2fa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49426.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49426
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
