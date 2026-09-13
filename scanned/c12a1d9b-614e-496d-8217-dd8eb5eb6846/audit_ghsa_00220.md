# [H] Regular Expression Denial of Service in no-case

## Summary
Severity: High
Advisory: GHSA-ff6r-5jwm-8292
CVE: CVE-2017-16099
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-ff6r-5jwm-8292
Type: github-advisory

## Affected
- npm: `no-case` — affected >=0 <2.3.2

## Details
Affected versions of `no-case` are vulnerable to a regular expression denial of service when parsing untrusted user input.


## Recommendation

Update to version 2.3.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16099
- https://github.com/blakeembrey/no-case/issues/17
- https://github.com/advisories/GHSA-ff6r-5jwm-8292
- https://www.npmjs.com/advisories/529
