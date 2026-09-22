# [M] Insecure Default Configuration in redbird

## Summary
Severity: Medium
Advisory: GHSA-8948-ffc6-jg52
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2019-06-06
Source: https://github.com/advisories/GHSA-8948-ffc6-jg52
Type: github-advisory

## Affected
- npm: `redbird` — affected >=0

## Details
Versions of `redbird` prior to 0.9.1 have a vulnerable default configuration of allowing TLS 1.0 connections on `lib/proxy.js`. The package does not provide an option to disable TLS 1.0 which is deprecated and vulnerable.


## Recommendation

Upgrade to version 0.9.1 or later.

## References
- https://github.com/OptimalBits/redbird/pull/207
- https://github.com/OptimalBits/redbird/commit/39c7a2da84a2ddddfe046ea80e98800518920516
- https://snyk.io/vuln/SNYK-JS-REDBIRD-174455
- https://www.npmjs.com/advisories/828
