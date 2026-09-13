# [H] Prototype Pollution in handlebars

## Summary
Severity: High
Advisory: GHSA-q42p-pg8m-cqh6
CWE: CWE-471
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2019-06-05
Source: https://github.com/advisories/GHSA-q42p-pg8m-cqh6
Type: github-advisory

## Affected
- npm: `handlebars` — affected >=4.1.0 <4.1.2
- npm: `handlebars` — affected >=4.0.0 <4.0.14
- npm: `handlebars` — affected >=0 <3.0.7

## Details
Versions of `handlebars` prior to 4.0.14 are vulnerable to Prototype Pollution. Templates may alter an Objects' prototype, thus allowing an attacker to execute arbitrary code on the server.


## Recommendation

For handlebars 4.1.x upgrade to 4.1.2 or later.
For handlebars 4.0.x upgrade to 4.0.14 or later.

## References
- https://github.com/handlebars-lang/handlebars.js/issues/1495
- https://github.com/handlebars-lang/handlebars.js/commit/0d6d8c335ad81bad1b672fc56b6a44f6aa472dac
- https://github.com/handlebars-lang/handlebars.js/commit/7372d4e9dffc9d70c09671aa28b9392a1577fd86
- https://github.com/handlebars-lang/handlebars.js/commit/85c8783b34fc6d36145d8b53885ad0b9e3c3f9c4
- https://github.com/handlebars-lang/handlebars.js/commit/cd38583216dce3252831916323202749431c773e
- https://snyk.io/vuln/SNYK-JS-HANDLEBARS-173692
- https://www.npmjs.com/advisories/755
