# [H] Cross-Site Scripting in @ionic/core

## Summary
Severity: High
Advisory: GHSA-r3xc-47qg-h929
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-r3xc-47qg-h929
Type: github-advisory

## Affected
- npm: `@ionic/core` — affected >=0 <4.0.3
- npm: `@ionic/core` — affected >=4.1.0 <4.1.3
- npm: `@ionic/core` — affected >=4.2.0 <4.2.1
- npm: `@ionic/core` — affected >=4.3.0 <4.3.1

## Details
Versions of  `@ionic/core` prior to 4.0.3, 4.1.3, 4.2.1 or 4.3.1 are vulnerable to Cross-Site Scripting (XSS). The package uses the unsafe `innerHTML` function without sanitizing input, which may allow attackers to execute arbitrary JavaScript on the victim's browser. This issue affects the components:
- `<ion-alert>.message`
- `<ion-searchbar>.placeholder`
- `<ion-infinite-scroll-content>.loadingText`
- `<ion-refresher-content>.pullingText`
- `<ion-refresher-content>.refershingText`


## Recommendation

- If you are using @ionic/core 4.0.x, upgrade to 4.0.3 or later.
- If you are using @ionic/core 4.1.x, upgrade to 4.1.3 or later.
- If you are using @ionic/core 4.2.x, upgrade to 4.2.1 or later.
- If you are using @ionic/core 4.3.x, upgrade to 4.3.1 or later.

## References
- https://github.com/ionic-team/ionic/issues/18065
- https://github.com/ionic-team/ionic
- https://www.npmjs.com/advisories/1023
