# [M] WebErpMesv2 has a File Upload Validation Bypass Leading to RCE

## Summary
Severity: Medium
Advisory: CVE-2026-22789
Aliases: GHSA-64rv-f829-x6m4
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-01-12
Source: https://osv.dev/vulnerability/CVE-2026-22789
Type: osv

## Details
WebErpMesv2 is a Resource Management and Manufacturing execution system Web for industry. Prior to 1.19, WebErpMesv2 contains a file upload validation bypass vulnerability in multiple controllers that allows authenticated users to upload arbitrary files, including PHP scripts, leading to Remote Code Execution (RCE). This vulnerability is identical in nature to CVE-2025-52130 but exists in different code locations that were not addressed by the original fix. This vulnerability is fixed in 1.19.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22789.json
- https://github.com/SMEWebify/WebErpMesv2/security/advisories/GHSA-64rv-f829-x6m4
- https://nvd.nist.gov/vuln/detail/CVE-2026-22789
- https://github.com/SMEWebify/WebErpMesv2/commit/c9e7f4a85aeb774a0ea4b61ad57a51b941166b69
