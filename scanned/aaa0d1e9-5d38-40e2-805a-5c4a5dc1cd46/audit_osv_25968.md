# [H] iTop vulnerable to potential formula injection in Excel/CSV export file

## Summary
Severity: High
Advisory: CVE-2023-48709
Aliases: GHSA-9q3x-9987-53x9
CVSS: 8.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-04-15
Source: https://osv.dev/vulnerability/CVE-2023-48709
Type: osv

## Details
iTop is an IT service management platform.  When exporting data from backoffice or portal in CSV or Excel files, users' inputs may include malicious formulas that may be imported into Excel. As Excel 2016 does **not** prevent Remote Code Execution by default, uninformed users may become victims. This vulnerability is fixed in 2.7.9, 3.0.4, 3.1.1, and 3.2.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/48xxx/CVE-2023-48709.json
- https://github.com/Combodo/iTop/security/advisories/GHSA-9q3x-9987-53x9
- https://nvd.nist.gov/vuln/detail/CVE-2023-48709
- https://github.com/Combodo/iTop/commit/083a0b79bfa2c106735b5c10eddb35a05ec7f04a
- https://github.com/Combodo/iTop/commit/b10bcb976dfe8e55aa0f659bfbcdd18334a1b17c
