# [M] Cross-Site Scripting in gitbook

## Summary
Severity: Medium
Advisory: GHSA-5h5r-23r4-m87h
CVE: CVE-2017-16019
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-5h5r-23r4-m87h
Type: github-advisory

## Affected
- npm: `gitbook` — affected >=0 <3.2.2

## Details
Affected versions of `gitbook` do not properly sanitize user input outside of backticks, which may result in cross-site scripting in the online reader.


## Recommendation

Update to version 3.2.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16019
- https://github.com/GitbookIO/gitbook/issues/1609
- https://www.npmjs.com/advisories/159
