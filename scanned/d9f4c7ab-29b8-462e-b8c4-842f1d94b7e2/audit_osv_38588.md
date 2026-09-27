# [H] Horilla: Unauthorized Document Overwrite via File Upload Endpoint

## Summary
Severity: High
Advisory: CVE-2026-40866
Aliases: GHSA-q2qh-v828-r4p7
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40866
Type: osv

## Details
Horilla is a free and open source Human Resource Management System (HRMS). In 1.5.0, an insecure direct object reference in the employee document upload endpoint allows any authenticated user to overwrite or replace or corrupt another employee’s document by changing the document ID in the upload request. This enables unauthorized modification of HR records.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40866.json
- https://github.com/horilla/horilla-hr/security/advisories/GHSA-q2qh-v828-r4p7
- https://nvd.nist.gov/vuln/detail/CVE-2026-40866
