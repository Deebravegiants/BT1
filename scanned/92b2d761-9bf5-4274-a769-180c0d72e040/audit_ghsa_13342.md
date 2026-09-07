# [M] matrix-react-sdk vulnerable to XSS in Export Chat feature

## Summary
Severity: Medium
Advisory: GHSA-c9vx-2g7w-rp65
CVE: CVE-2023-37259
CWE: CWE-79, CWE-80
Ecosystem: npm
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-18
Source: https://github.com/advisories/GHSA-c9vx-2g7w-rp65
Type: github-advisory

## Affected
- npm: `matrix-react-sdk` — affected >=3.32.0 <3.76.0

## Details
### Description

The Export Chat feature includes certain attacker-controlled elements in the generated document without sufficient escaping, leading to stored XSS.

### Impact

Since the Export Chat feature generates a separate document, an attacker can only inject code run from the `null` origin, restricting the impact.

However, the attacker can still potentially use the XSS to leak message contents. A malicious homeserver is a potential attacker since the affected inputs are controllable server-side.

### Patches
This was patched in matrix-react-sdk 3.76.0.

### Workarounds
None, other than not using the Export Chat feature.

### References
N/A

## References
- https://github.com/matrix-org/matrix-react-sdk/security/advisories/GHSA-c9vx-2g7w-rp65
- https://nvd.nist.gov/vuln/detail/CVE-2023-37259
- https://github.com/matrix-org/matrix-react-sdk/commit/22fcd34c606f32129ebc967fc21f24fb708a98b8
- https://github.com/matrix-org/matrix-react-sdk
- https://github.com/matrix-org/matrix-react-sdk/releases/tag/v3.76.0
