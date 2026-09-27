# [C] SQL Injection and Cross-site Scripting in class-validator

## Summary
Severity: Critical
Advisory: GHSA-fj58-h2fr-3pp2
CVE: CVE-2019-18413
CWE: CWE-79, CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-fj58-h2fr-3pp2
Type: github-advisory

## Affected
- npm: `class-validator` — affected >=0 <0.14.0

## Details
In TypeStack class-validator, `validate()` input validation can be bypassed because certain internal attributes can be overwritten via a conflicting name. Even though there is an optional `forbidUnknownValues` parameter that can be used to reduce the risk of this bypass, this option is not documented and thus most developers configure input validation in the vulnerable default manner. With this vulnerability, attackers can launch SQL Injection or XSS attacks by injecting arbitrary malicious input.

The default settings for `forbidUnknownValues` has been changed to `true` in 0.14.0.

NOTE: a software maintainer agrees with the "is not documented" finding but suggests that much of the responsibility for the risk lies in a different product.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-18413
- https://github.com/typestack/class-validator/issues/1422#issuecomment-1344635415
- https://github.com/typestack/class-validator/issues/438
- https://github.com/typestack/class-validator/issues/438#issuecomment-964728471
- https://github.com/typestack/class-validator/pull/1798
- https://github.com/typestack/class-validator
- https://github.com/typestack/class-validator#passing-options
