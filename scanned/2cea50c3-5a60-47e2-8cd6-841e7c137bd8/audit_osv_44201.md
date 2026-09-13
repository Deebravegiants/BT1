# [H] drm/shmem_helper: Check VMA boundaries for PMD mappings

## Summary
Severity: High
Advisory: CVE-2026-80582
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80582
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.0.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/shmem_helper: Check VMA boundaries for PMD mappings

In the ->huge_fault handler do not install a PMD huge page
mapping if the huge page exceeds the boundaries of the VMA.

All other ->huge_fault handlers have similar checks and the
resulting mapping will trigger a VM_BUG_ON_VMA() if it ever
reaches copy_pmd_range().

## References
- https://git.kernel.org/stable/c/12803e89a1e593fd1e784dfe7453f5e392ccaff2
- https://git.kernel.org/stable/c/617bbd08714857c1613d7c550d43a9092ec0fb97
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80582.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80582
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
