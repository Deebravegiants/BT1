# [M] exceljs through 4.4.0 CSV Formula Injection via Unescaped Cell Values

## Summary
Severity: Medium
Advisory: CVE-2026-78209
Aliases: GHSA-9wxc-4rhw-hfrw
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-78209
Type: osv

## Details
exceljs through 4.4.0 fails to neutralize leading equals, plus, minus, or at signs in cell values written to CSV output. Attackers who can influence exported cell values can inject formulas that execute when the CSV file is opened in a spreadsheet application, potentially exfiltrating data or performing other malicious actions.

## References
- https://www.npmjs.com/package/exceljs
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78209.json
- https://github.com/mateocallec/exceljs-hardened/security/advisories/GHSA-9wxc-4rhw-hfrw
- https://nvd.nist.gov/vuln/detail/CVE-2026-78209
- https://www.vulncheck.com/advisories/exceljs-through-csv-formula-injection-via-unescaped-cell-values
- https://github.com/exceljs/exceljs
- https://github.com/exceljs/exceljs/blob/v4.4.0/lib/csv/csv.js#L109-L182
