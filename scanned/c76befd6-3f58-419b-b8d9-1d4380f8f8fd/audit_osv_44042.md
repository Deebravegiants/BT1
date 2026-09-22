# [M] exceljs through 4.4.0 Path Traversal via Unvalidated addImage filename

## Summary
Severity: Medium
Advisory: CVE-2026-78208
Aliases: GHSA-m8mg-8574-gm3m
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-78208
Type: osv

## Details
exceljs through 4.4.0 contains a path traversal vulnerability in the Workbook.addImage() function that fails to validate file paths. Attackers can supply arbitrary file paths to read any file accessible to the Node.js process and embed it in the generated workbook.

## References
- https://www.npmjs.com/package/exceljs
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78208.json
- https://github.com/mateocallec/exceljs-hardened/security/advisories/GHSA-m8mg-8574-gm3m
- https://nvd.nist.gov/vuln/detail/CVE-2026-78208
- https://www.vulncheck.com/advisories/exceljs-through-path-traversal-via-unvalidated-addimage-filename
- https://github.com/exceljs/exceljs
- https://github.com/exceljs/exceljs/blob/v4.4.0/lib/doc/workbook.js#L142-L147
- https://github.com/exceljs/exceljs/blob/v4.4.0/lib/xlsx/xlsx.js#L421-L429
