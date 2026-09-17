# [M] DataEase ExportCenter IDOR allows cross-user export task access

## Summary
Severity: Medium
Advisory: CVE-2026-53729
Aliases: GHSA-9423-78gr-xjj5
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-53729
Type: osv

## Details
DataEase is an open source data visualization and analysis tool. Prior to 2.10.24, any authenticated user can download (/exportCenter/download/{id}), delete (/exportCenter/delete), retry (/exportCenter/retry/{id}), or generate download links (/exportCenter/generateDownloadUri/{id}) for export tasks belonging to other users by manipulating the task ID parameter, and the /exportCenter/download/{id} endpoint is whitelisted from authentication, allowing unauthenticated access to exported files. This issue is fixed in version 2.10.24.

## References
- https://github.com/dataease/dataease/releases/tag/v2.10.24
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53729.json
- https://github.com/dataease/dataease/security/advisories/GHSA-9423-78gr-xjj5
- https://nvd.nist.gov/vuln/detail/CVE-2026-53729
- https://github.com/dataease/dataease/commit/57e90bdcc21c3fa2ec57184671603ad88a5b941b
