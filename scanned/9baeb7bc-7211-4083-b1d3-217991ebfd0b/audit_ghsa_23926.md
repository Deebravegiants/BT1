# [C] Use After Free in Hermes

## Summary
Severity: Critical
Advisory: GHSA-mph8-6787-r8hw
CVE: CVE-2021-24037
CWE: CWE-416
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-mph8-6787-r8hw
Type: github-advisory

## Affected
- npm: `hermes-engine` — affected >=0 <0.8.0

## Details
A use after free in hermes, while emitting certain error messages, prior to commit d86e185e485b6330216dee8e854455c694e3a36e allows attackers to potentially execute arbitrary code via crafted JavaScript. Note that this is only exploitable if the application using Hermes permits evaluation of untrusted JavaScript. Hence, most React Native applications are not affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-24037
- https://github.com/facebook/hermes/commit/d86e185e485b6330216dee8e854455c694e3a36e
- https://github.com/facebook/hermes
- https://www.facebook.com/security/advisories/CVE-2021-24037
