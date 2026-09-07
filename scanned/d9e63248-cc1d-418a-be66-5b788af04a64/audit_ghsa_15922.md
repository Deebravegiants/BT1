# [M] Knwl.js Regular Expression Denial of Service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-68qg-g787-3rp5
CVE: CVE-2020-26306
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U/U:Green (CVSS_V4)
Published: 2024-10-26
Source: https://github.com/advisories/GHSA-68qg-g787-3rp5
Type: github-advisory

## Affected
- npm: `knwl.js` — affected >=0

## Details
Knwl.js is a Javascript library that parses through text for dates, times, phone numbers, emails, places, and more. Versions 1.0.2 and prior contain one or more regular expressions that are vulnerable to Regular Expression Denial of Service (ReDoS). As of time of publication, no known patches are available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-26306
- https://github.com/benhmoore/Knwl/issues/106
- https://github.com/benhmoore/Knwl/commit/88aa966b1415a167c7c91b70053b72c7762c1cc0
- https://github.com/benhmoore/Knwl
- https://securitylab.github.com/advisories/GHSL-2020-296-redos-Knwl.js
