# [M] LORIS has incorrect access checks in document_repository

## Summary
Severity: Medium
Advisory: CVE-2026-35165
Aliases: GHSA-qp6x-qfx7-54wp
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-35165
Type: osv

## Details
LORIS (Longitudinal Online Research and Imaging System) is a self-hosted web application that provides data- and project-management for neuroimaging research. From 21.0.0 to before 27.0.3 and 28.0.1, while the document_repository frontend was restricting file access, the backend endpoint was not correctly verifying access permissions. A user could theoretically download a file that they should not have access to, if they know or can brute force the filename. This vulnerability is fixed in 27.0.3 and 28.0.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35165.json
- https://github.com/aces/Loris/security/advisories/GHSA-qp6x-qfx7-54wp
- https://nvd.nist.gov/vuln/detail/CVE-2026-35165
