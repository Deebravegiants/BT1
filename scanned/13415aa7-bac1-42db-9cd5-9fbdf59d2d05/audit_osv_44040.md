# [M] exceljs through 4.4.0 Uncontrolled Resource Consumption via Unbounded xlsx Decompression

## Summary
Severity: Medium
Advisory: CVE-2026-78206
Aliases: GHSA-7cvf-3r55-r39q
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-78206
Type: osv

## Details
exceljs through 4.4.0 decompresses all entries from supplied xlsx archives into memory without limits on entry size, total size, or compression ratio. Attackers can upload highly compressed workbooks that expand to gigabytes in memory, exhausting available resources and causing denial of service.

## References
- https://www.npmjs.com/package/exceljs
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78206.json
- https://github.com/mateocallec/exceljs-hardened/security/advisories/GHSA-7cvf-3r55-r39q
- https://nvd.nist.gov/vuln/detail/CVE-2026-78206
- https://www.vulncheck.com/advisories/exceljs-through-uncontrolled-resource-consumption-via-unbounded-xlsx-decompression
- https://github.com/exceljs/exceljs
- https://github.com/exceljs/exceljs/blob/v4.4.0/lib/xlsx/xlsx.js#L257-L281
