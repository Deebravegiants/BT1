# [H] Cross-Site Scripting in htmr

## Summary
Severity: High
Advisory: GHSA-f8rq-m28h-8hxj
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-f8rq-m28h-8hxj
Type: github-advisory

## Affected
- npm: `htmr` — affected >=0 <0.8.7

## Details
Versions of `htmr` prior to 0.8.7 are vulnerable to Cross-Site Scripting (XSS).  The package uses `innerHTML` to unescape HTML entities. This may lead to [DOM-based XSS](https://owasp.org/www-community/attacks/DOM_Based_XSS) through HTML-encoded XSS payloads. This may allow an attacker to execute arbitrary JavaScript in a victim's browser.


## Recommendation

Upgrade to version 0.8.7 or later.

## References
- https://hackerone.com/reports/753971
- https://www.npmjs.com/advisories/1496
