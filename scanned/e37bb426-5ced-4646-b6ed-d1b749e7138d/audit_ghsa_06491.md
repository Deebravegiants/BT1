# [M] showdown allows stored cross-site scripting through table header ID injection

## Summary
Severity: Medium
Advisory: GHSA-22g5-r2x5-97cx
CVE: CVE-2026-59710
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-07
Source: https://github.com/advisories/GHSA-22g5-r2x5-97cx
Type: github-advisory

## Affected
- npm: `showdown` — affected >=0

## Details
showdown contains a stored cross-site scripting vulnerability in the parseHeaders function of src/subParsers/makehtml/tables.js that fails to properly escape table header ID attributes. Attackers can inject arbitrary HTML and script-executing SVG elements through double-quote characters in markdown table headers, achieving stored XSS when untrusted markdown is rendered with the default github flavor configuration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-59710
- https://github.com/showdownjs/showdown/issues/1046
- https://github.com/showdownjs/showdown/commit/e5cab1e9a5dcea2bb3cbf888863fa7e65ab37edf
- https://github.com/showdownjs/showdown
- https://www.vulncheck.com/advisories/showdown-stored-xss-via-unescaped-table-header-id-attribute-injection
