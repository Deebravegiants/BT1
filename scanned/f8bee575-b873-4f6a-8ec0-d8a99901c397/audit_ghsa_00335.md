# [M] Regular Expression Denial of Service in slug

## Summary
Severity: Medium
Advisory: GHSA-jxqq-cqm6-pfq9
CVE: CVE-2017-16117
CWE: CWE-400
Ecosystem: npm
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-jxqq-cqm6-pfq9
Type: github-advisory

## Affected
- npm: `slug` — affected >=0 <0.9.2

## Details
Affected versions of `slug` are vulnerable to a regular expression denial of service when parsing untrusted user input.

The issue is low severity, as it takes 50,000 characters to cause the event loop to block for 2 seconds,

About 50k characters can block the event loop for 2 seconds.


## Recommendation

Update to version 0.9.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16117
- https://github.com/dodo/node-slug/issues/82
- https://github.com/advisories/GHSA-jxqq-cqm6-pfq9
- https://www.npmjs.com/advisories/537
