# [H] Cross-Site Scripting in bootstrap-select

## Summary
Severity: High
Advisory: GHSA-9r7h-6639-v5mw
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-9r7h-6639-v5mw
Type: github-advisory

## Affected
- npm: `bootstrap-select` — affected >=0 <1.13.6

## Details
Versions of `bootstrap-select` prior to 1.13.6 are vulnerable to Cross-Site Scripting (XSS).  The package does not escape `title` values on `<option>` tags. This may allow attackers to execute arbitrary JavaScript in a victim's browser.


## Recommendation

Upgrade to version 1.13.6 or later.

## References
- https://github.com/dimpu/ngx-md/issues/129
- https://github.com/snapappointments/bootstrap-select/issues/2199
- https://github.com/snapappointments/bootstrap-select
- https://www.npmjs.com/advisories/1522
