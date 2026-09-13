# [H] Regular Expression Denial of Service in fresh

## Summary
Severity: High
Advisory: GHSA-9qj9-36jm-prpv
CVE: CVE-2017-16119
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-9qj9-36jm-prpv
Type: github-advisory

## Affected
- npm: `fresh` — affected >=0 <0.5.2

## Details
Affected versions of `fresh` are vulnerable to regular expression denial of service when parsing specially crafted user input.


## Recommendation

Update to version 0.5.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16119
- https://github.com/advisories/GHSA-9qj9-36jm-prpv
- https://www.npmjs.com/advisories/526
