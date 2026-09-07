# [M] Cross-Site Scripting in exceljs

## Summary
Severity: Medium
Advisory: GHSA-2j2j-8rrv-264g
CVE: CVE-2018-16459
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-09-11
Source: https://github.com/advisories/GHSA-2j2j-8rrv-264g
Type: github-advisory

## Affected
- npm: `exceljs` — affected >=0 <1.6.0

## Details
Versions of `exceljs` before 1.6.0 are vulnerable to cross-site scripting. 

This vulnerability is due to `exceljs` not validating data from parsed XLSX file and embedding HTML tags, like `<script>` directly into the sheet cells. Because of this it's possible to inject malicious JavaScript code and execute it when data from the sheet is displayed in the browser.




## Recommendation

Update to version 1.6.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16459
- https://hackerone.com/reports/356809
- https://github.com/advisories/GHSA-2j2j-8rrv-264g
- https://github.com/nodejs/security-wg/blob/master/vuln/npm/464.json
- https://www.npmjs.com/advisories/733
