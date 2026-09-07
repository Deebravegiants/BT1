# [H] Prototype Pollution in sheetJS

## Summary
Severity: High
Advisory: GHSA-4r6h-8v6p-xvw6
CVE: CVE-2023-30533
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-24
Source: https://github.com/advisories/GHSA-4r6h-8v6p-xvw6
Type: github-advisory

## Affected
- npm: `xlsx` — affected >=0

## Details
All versions of SheetJS CE through 0.19.2 are vulnerable to "Prototype Pollution" when reading specially crafted files. Workflows that do not read arbitrary files (for example, exporting data to spreadsheet files) are unaffected.

A non-vulnerable version cannot be found via npm, as the repository hosted on GitHub and the npm package `xlsx` are no longer maintained. Version 0.19.3 can be downloaded via https://cdn.sheetjs.com/.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30533
- https://cdn.sheetjs.com
- https://cdn.sheetjs.com/advisories/CVE-2023-30533
- https://git.sheetjs.com/sheetjs/sheetjs
- https://git.sheetjs.com/sheetjs/sheetjs/issues/2667
- https://git.sheetjs.com/sheetjs/sheetjs/issues/2986
- https://git.sheetjs.com/sheetjs/sheetjs/src/branch/master/CHANGELOG.md
