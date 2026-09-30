# [M] Horilla Exposes Unpublished Job Disclosures through Unauthenticated API

## Summary
Severity: Medium
Advisory: CVE-2026-24036
Aliases: GHSA-q4xr-w96p-3vg7
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-01-22
Source: https://osv.dev/vulnerability/CVE-2026-24036
Type: osv

## Details
Horilla is a free and open source Human Resource Management System (HRMS). Versions 1.4.0 and above expose unpublished job postings through the /recruitment/recruitment-details// endpoint without authentication. The response includes draft job titles, descriptions and application link allowing unauthenticated users to view unpublished roles and access the application workflow for unpublished jobs. Unauthorized access to unpublished job posts can leak sensitive internal hiring information and cause confusion among candidates. This issue has been fixed in version 1.5.0.

## References
- https://github.com/horilla-opensource/horilla/releases/tag/1.5.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24036.json
- https://github.com/horilla-opensource/horilla/security/advisories/GHSA-q4xr-w96p-3vg7
- https://nvd.nist.gov/vuln/detail/CVE-2026-24036
- https://github.com/horilla-opensource/horilla/commit/9a585a1588431499092a49d7e82cb77daa4d99ee
