# [M] element-plus vulnerable to cross-site scripting (XSS) via el-table-column

## Summary
Severity: Medium
Advisory: GHSA-rjvg-8v36-xv9r
CVE: CVE-2022-27103
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-26
Source: https://github.com/advisories/GHSA-rjvg-8v36-xv9r
Type: github-advisory

## Affected
- npm: `element-plus` — affected >=0 <2.0.6

## Details
element-plus below 2.0.5 is vulnerable to Cross Site Scripting (XSS) when attribute `show-tooltips-overflow` of `el-table-column` is true. The mouseover action will make the text of this column render as html.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27103
- https://github.com/asjdf/element-table-xss-test/issues/1
- https://github.com/element-plus/element-plus/issues/6514
- https://github.com/element-plus/element-plus/pull/6520
- https://github.com/element-plus/element-plus/commit/063c56446135176971f532bd0eb2e88a0b137d43
- https://github.com/asjdf/element-table-xss-test
- https://github.com/element-plus/element-plus
