# [M] Arbitrary File Write in adm-zip

## Summary
Severity: Medium
Advisory: GHSA-3v6h-hqm4-2rg6
CVE: CVE-2018-1002204
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-07-27
Source: https://github.com/advisories/GHSA-3v6h-hqm4-2rg6
Type: github-advisory

## Affected
- npm: `adm-zip` — affected >=0 <0.4.11

## Details
Versions of `adm-zip` before 0.4.9 are vulnerable to arbitrary file write when used to extract a specifically crafted archive that contains path traversal filenames (`../../file.txt` for example).


## Recommendation

Update to version 0.4.9 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1002204
- https://github.com/cthackers/adm-zip/pull/212
- https://github.com/cthackers/adm-zip/commit/62f64004fefb894c523a7143e8a88ebe6c84df25
- https://hackerone.com/reports/362118
- https://github.com/advisories/GHSA-3v6h-hqm4-2rg6
- https://github.com/snyk/zip-slip-vulnerability
- https://snyk.io/research/zip-slip-vulnerability
- https://snyk.io/vuln/npm:adm-zip:20180415
- https://www.npmjs.com/advisories/681
- https://www.npmjs.com/advisories/994
- http://www.securityfocus.com/bid/107001
