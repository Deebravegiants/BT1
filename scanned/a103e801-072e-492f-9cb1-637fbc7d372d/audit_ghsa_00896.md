# [M] Configuration Override in helmet-csp

## Summary
Severity: Medium
Advisory: GHSA-c3m8-x3cg-qm2c
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-c3m8-x3cg-qm2c
Type: github-advisory

## Affected
- npm: `helmet-csp` — affected >=1.2.2 <2.9.1

## Details
Versions of `helmet-csp` before to 2.9.1 are vulnerable to a Configuration Override affecting the application's Content Security Policy (CSP). The package's browser sniffing for Firefox deletes the `default-src` CSP policy, which is the fallback policy. This allows an attacker to remove an application's default CSP, possibly rendering the application vulnerable to Cross-Site Scripting.


## Recommendation

Upgrade to version 2.9.1 or later. Setting the `browserSniff` configuration to `false` in vulnerable versions also mitigates the issue.

## References
- https://github.com/helmetjs/csp/commit/67a69baafa8198a154f0505a0cf0875f76f6186a
- https://github.com/helmetjs/csp
- https://snyk.io/vuln/SNYK-JS-HELMETCSP-469436
- https://www.npmjs.com/advisories/1176
