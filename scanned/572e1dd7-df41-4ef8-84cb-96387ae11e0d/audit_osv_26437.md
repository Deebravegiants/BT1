# [M] driver core: location: Free struct acpi_pld_info *pld before return false

## Summary
Severity: Medium
Advisory: CVE-2023-53211
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53211
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

driver core: location: Free struct acpi_pld_info *pld before return false

struct acpi_pld_info *pld should be freed before the return of allocation
failure, to prevent memory leak, add the ACPI_FREE() to fix it.

## References
- https://git.kernel.org/stable/c/0d150f967e8410e1e6712484543eec709356a65d
- https://git.kernel.org/stable/c/5a9de90951bbeaed775e4b8d1b16b4d359e82bf5
- https://git.kernel.org/stable/c/8fe72b8f59f63ca776bb8a4fcd2f406057a9fc90
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53211.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53211
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
