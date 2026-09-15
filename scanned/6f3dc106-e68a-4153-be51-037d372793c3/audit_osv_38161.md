# [M] LORIS has incorrect access checks in media module

## Summary
Severity: Medium
Advisory: CVE-2026-34985
Aliases: GHSA-p42c-4gmq-hrjw
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-34985
Type: osv

## Details
LORIS (Longitudinal Online Research and Imaging System) is a self-hosted web application that provides data- and project-management for neuroimaging research. From 16.1.0 to before 27.0.3 and 28.0.1, While the frontend of the media module filters files that the user should not have access to, the backend was not applying access checks and it would be possible for someone who should not have access to a file to access it if they know the filename. This vulnerability is fixed in 27.0.3 and 28.0.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34985.json
- https://github.com/aces/Loris/security/advisories/GHSA-p42c-4gmq-hrjw
- https://nvd.nist.gov/vuln/detail/CVE-2026-34985
