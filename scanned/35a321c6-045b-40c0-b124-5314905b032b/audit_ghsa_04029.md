# [M] Cross-Site Scripting in backbone

## Summary
Severity: Medium
Advisory: GHSA-j6p2-cx3w-6jcp
CVE: CVE-2016-10537
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-j6p2-cx3w-6jcp
Type: github-advisory

## Affected
- npm: `backbone` — affected >=0.3.3 <0.5.0

## Details
Affected versions of `backbone` are vulnerable to cross-site scripting when users are allowed to supply input to the `Model#Escape` function, and the output is then written to the DOM. 

The vulnerability occurs as a result of the regular expression used to encode metacharacters failing to take HTML Entities such as `&#60;` into account.


## Recommendation

Update to version 0.5.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10537
- https://github.com/jashkenas/backbone/commit/0cdc525961d3fa98e810ffae6bcc8e3838e36d93
- https://github.com/jashkenas/backbone/commit/7ae0384120c2552e1c426cda7fb02fdce6ef1076
- https://backbonejs.org/#changelog
- https://github.com/jashkenas/backbone
- https://github.com/jashkenas/backbone/blame/0cdc525961d3fa98e810ffae6bcc8e3838e36d93/backbone.js
- https://github.com/jashkenas/backbone/compare/0.3.3...0.5.0#diff-0d56d0d310de7ff18b3cef9c2f8f75dcL1008
