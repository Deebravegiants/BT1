# [M] Cross-Site Scripting in @berslucas/liljs

## Summary
Severity: Medium
Advisory: GHSA-c53x-wwx2-pg96
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-c53x-wwx2-pg96
Type: github-advisory

## Affected
- npm: `@berslucas/liljs` — affected >=0 <1.0.2

## Details
Versions of  `@berslucas/liljs` prior to 1.0.2 are vulnerable to Cross-Site Scripting (XSS). The package uses the unsafe `innerHTML` function without sanitizing input, which may allow attackers to execute arbitrary JavaScript on the victim's browser.


## Recommendation

Upgrade to version 1.0.2 or later.

## References
- https://github.com/bersLucas/liljs/pull/7
- https://github.com/bersLucas/liljs/commit/779c0dcd8aba434a1c94db7d1d2d990a629f9a6c
- https://github.com/bersLucas/liljs
- https://github.com/bersLucas/liljs/releases/tag/1.0.2
- https://snyk.io/vuln/SNYK-JS-BERSLUCASLILJS-450217
- https://www.npmjs.com/advisories/1016
