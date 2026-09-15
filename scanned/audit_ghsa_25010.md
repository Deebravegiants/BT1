# [C] Always-Incorrect Control Flow Implementation in Facebook Hermes

## Summary
Severity: Critical
Advisory: GHSA-327c-qx3v-h673
CVE: CVE-2020-1914
CWE: CWE-1119, CWE-670
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-327c-qx3v-h673
Type: github-advisory

## Affected
- npm: `hermes-engine` — affected >=0 <0.7.2

## Details
A logic vulnerability when handling the SaveGeneratorLong instruction in Facebook Hermes prior to commit b2021df620824627f5a8c96615edbd1eb7fdddfc allows attackers to potentially read out of bounds or theoretically execute arbitrary code via crafted JavaScript. Note that this is only exploitable if the application using Hermes permits evaluation of untrusted JavaScript. Hence, most React Native applications are not affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1914
- https://github.com/facebook/hermes/issues/373
- https://github.com/facebook/hermes/commit/b2021df620824627f5a8c96615edbd1eb7fdddfc
- https://github.com/facebook/hermes
- https://www.facebook.com/security/advisories/cve-2020-1914
