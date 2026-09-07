# [H] XSS in client rendered block templates in rendr

## Summary
Severity: High
Advisory: GHSA-v5hp-35hw-cw5x
CVE: CVE-2016-1000230
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-v5hp-35hw-cw5x
Type: github-advisory

## Affected
- npm: `rendr` — affected >=0 <1.1.4

## Details
Affected versions of `rendr` are vulnerable to cross-site scripting when client side rendering is done inside a `_block`.

Server side rendering is not affected and is properly escaped.


## Recommendation

Update to version 1.1.4 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1000230
- https://github.com/rendrjs/rendr-handlebars/pull/61
- https://github.com/rendrjs/rendr/pull/513
- https://github.com/rendrjs/rendr-handlebars
- https://www.npmjs.com/advisories/128
