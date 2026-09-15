# [M] drm/tegra: Fix NULL vs IS_ERR() check in probe()

## Summary
Severity: Medium
Advisory: CVE-2024-53078
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53078
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/tegra: Fix NULL vs IS_ERR() check in probe()

The iommu_paging_domain_alloc() function doesn't  return NULL pointers,
it returns error pointers.  Update the check to match.

## References
- https://git.kernel.org/stable/c/6d6c005855b97b8caf6039c1774745ee74c91fa6
- https://git.kernel.org/stable/c/a85df8c7b5ee2d3d4823befada42c5c41aff4cb0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53078.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53078
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
