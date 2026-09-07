# [H] Regular Expression Denial of Service in content

## Summary
Severity: High
Advisory: GHSA-x6wp-rfwh-hcx7
CVE: CVE-2017-16111
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-x6wp-rfwh-hcx7
Type: github-advisory

## Affected
- npm: `content` — affected >=0 <3.0.7

## Details
Affected versions of `content` are vulnerable to a regular expression denial of service when parsing malicious `Content-Type` and `Content-Disposition` headers.


## Recommendation

Update to version 3.0.6 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16111
- https://github.com/advisories/GHSA-x6wp-rfwh-hcx7
- https://www.npmjs.com/advisories/530
