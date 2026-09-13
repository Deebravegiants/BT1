# [H] Stirling-PDF Zip Slip: Arbitrary File Write via Path Traversal in Markdown-to-PDF ZIP Extraction

## Summary
Severity: High
Advisory: CVE-2026-27625
Aliases: GHSA-wccq-mg6x-2w22
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-27625
Type: osv

## Details
Stirling-PDF is a locally hosted web application that performs various operations on PDF files. In versions prior to 2.5.2, the /api/v1/convert/markdown/pdf endpoint extracts user-supplied ZIP entries without path checks. Any authenticated user can write files outside the intended temporary working directory, leading to arbitrary file write with the privileges of the Stirling-PDF process user (stirlingpdfuser). This can overwrite writable files and compromise data integrity, with further impact depending on writable paths. The issue was fixed in version 2.5.2.

## References
- https://github.com/Stirling-Tools/Stirling-PDF/releases/tag/v2.5.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27625.json
- https://github.com/Stirling-Tools/Stirling-PDF/security/advisories/GHSA-wccq-mg6x-2w22
- https://nvd.nist.gov/vuln/detail/CVE-2026-27625
