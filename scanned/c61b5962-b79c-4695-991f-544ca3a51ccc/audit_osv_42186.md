# [M] Velociraptor CSV Formula Injection in Export Pipeline

## Summary
Severity: Medium
Advisory: CVE-2026-64955
CVSS: 6.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:N/A:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-64955
Type: osv

## Details
When Microsoft Excel imports a CSV file, it executes cells beginning with certain characters as formulas, giving such CSV files arbitrary execution. 

Velociraptor fails to sanitize such cells when exporting to CSV from various places such as the GUI, offline collector or data exports.

It is not clear if the vulnerability is actually in Microsoft Excel treating a CSV data file as executable content, or if Velociraptor should be sanitizing the data to prevent Excel from executing it. However, since this is such a common use case for Velociraptor we decided to highlight it in an advisory.

## References
- https://github.com/Velocidex/velociraptor/
- http://docs.velociraptor.app/announcements/advisories/cve-2026-64955/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64955.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64955
