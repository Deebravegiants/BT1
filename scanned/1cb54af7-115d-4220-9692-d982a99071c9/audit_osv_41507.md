# [M] SolidInvoice allows cross-user access to API token request history via writable DataGrid LiveComponent props

## Summary
Severity: Medium
Advisory: CVE-2026-61688
Aliases: GHSA-jhv9-9fv9-67cr
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-61688
Type: osv

## Details
SolidInvoice is an open-source invoicing platform. Prior to version 3.0.1, an authenticated user can view the API request history of any other user's API tokens within the same company by manipulating two writable Symfony UX LiveComponent props on the `DataGrid` component. Version 3.0.1 fixes the issue.

## References
- https://github.com/SolidInvoice/SolidInvoice/releases/tag/3.0.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61688.json
- https://github.com/SolidInvoice/SolidInvoice/security/advisories/GHSA-jhv9-9fv9-67cr
- https://nvd.nist.gov/vuln/detail/CVE-2026-61688
