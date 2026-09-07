# [H] Cross-Site Scripting in graylog-web-interface

## Summary
Severity: High
Advisory: GHSA-9qgh-7pgp-hp7r
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-9qgh-7pgp-hp7r
Type: github-advisory

## Affected
- npm: `graylog-web-interface` — affected >=0.0.0

## Details
All versions of  `graylog-web-interface` are vulnerable to Cross-Site Scripting (XSS). The package fails to escape output on the `TypeAhead` and `QueryInput` components, which may allow attackers to execute arbitrary JavaScript on the victim's browser.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://www.npmjs.com/advisories/1028
