# [H] Out-of-bounds Read in Facebook Hermes

## Summary
Severity: High
Advisory: GHSA-x4cf-6jr3-3qvp
CVE: CVE-2020-1915
CWE: CWE-125
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-x4cf-6jr3-3qvp
Type: github-advisory

## Affected
- npm: `hermes-engine` — affected >=0 <0.7.2

## Details
An out-of-bounds read in the JavaScript Interpreter in Facebook Hermes prior to commit 8cb935cd3b2321c46aa6b7ed8454d95c75a7fca0 allows attackers to cause a denial of service attack or possible further memory corruption via crafted JavaScript. Note that this is only exploitable if the application using Hermes permits evaluation of untrusted JavaScript. Hence, most React Native applications are not affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1915
- https://github.com/facebook/hermes/issues/373
- https://github.com/facebook/hermes/commit/8cb935cd3b2321c46aa6b7ed8454d95c75a7fca0
- https://github.com/facebook/hermes
- https://www.facebook.com/security/advisories/cve-2020-1915
