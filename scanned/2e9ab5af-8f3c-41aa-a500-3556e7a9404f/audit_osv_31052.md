# [M] scsi: ufs: pltfrm: Dellocate HBA during ufshcd_pltfrm_remove()

## Summary
Severity: Medium
Advisory: CVE-2024-57872
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-57872
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: ufs: pltfrm: Dellocate HBA during ufshcd_pltfrm_remove()

This will ensure that the scsi host is cleaned up properly using
scsi_host_dev_release(). Otherwise, it may lead to memory leaks.

## References
- https://git.kernel.org/stable/c/897df60c16d54ad515a3d0887edab5c63da06d1f
- https://git.kernel.org/stable/c/cd188519d2467ab4c2141587b0551ba030abff0e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57872.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57872
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
