# [M] Cross-Site Scripting in @hapi/boom

## Summary
Severity: Medium
Advisory: GHSA-2ggq-vfcp-gwhj
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-2ggq-vfcp-gwhj
Type: github-advisory

## Affected
- npm: `@hapi/boom` — affected >=0 <0.3.8

## Details
Versions of `@hapi/boom` prior to 0.3.8 are vulnerable to Cross-Site Scripting (XSS). The package fails to properly escape error messages, which may allow attackers to execute arbitrary JavaScript in a victim's browser.


## Recommendation

Upgrade to version 0.3.8 or later.

## References
- https://github.com/hapijs/boom/commit/0f8640bdba65aec6e6799bfc16ff5753150bfcaf
- https://github.com/hapijs/boom
- https://snyk.io/vuln/SNYK-JS-HAPIBOOM-541183
