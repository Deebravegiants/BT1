# [H] Regular Expression Denial of Service in forwarded

## Summary
Severity: High
Advisory: GHSA-mpcf-4gmh-23w8
CVE: CVE-2017-16118
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-mpcf-4gmh-23w8
Type: github-advisory

## Affected
- npm: `forwarded` — affected >=0 <0.1.2

## Details
Affected versions of `forwarded` are vulnerable to regular expression denial of service when parsing specially crafted user input.


## Recommendation

Update to version 0.1.2 or later

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16118
- https://github.com/advisories/GHSA-mpcf-4gmh-23w8
- https://www.npmjs.com/advisories/527
- http://www.securityfocus.com/bid/104427
