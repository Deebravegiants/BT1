# [H] Cross-Site Scripting in ngx-md

## Summary
Severity: High
Advisory: GHSA-xr53-m937-jr9c
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-xr53-m937-jr9c
Type: github-advisory

## Affected
- npm: `ngx-md` — affected >=0 <6.0.3

## Details
Versions of `ngx-md` prior to 6.0.3 are vulnerable to Cross-Site Scripting.  Links are not properly restricted to http/https and can contain JavaScript which may lead to arbitrary code execution. Markdown input such as `[Click Me](javascript:alert('Injected!'%29)` is rendered as a `Click Me` link that executes JavaScript.


## Recommendation

Upgrade to version 6.0.3 or later.

## References
- https://github.com/dimpu/ngx-md/issues/129
- https://github.com/dimpu/ngx-md
- https://www.npmjs.com/advisories/1485
