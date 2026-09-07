# [H] Cross-Site Scripting in eco

## Summary
Severity: High
Advisory: GHSA-r32x-jhw5-g48p
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-r32x-jhw5-g48p
Type: github-advisory

## Affected
- npm: `eco` — affected >=0.0.0

## Details
All versions of  `eco` are vulnerable to Cross-Site Scripting (XSS). The package's default `__escape` implementation fails to escape single quotes, which may allow attackers to execute arbitrary JavaScript on the victim's browser.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://github.com/sstephenson/eco/pull/67
- https://github.com/sstephenson/eco
- https://www.npmjs.com/advisories/1024
