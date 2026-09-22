# [M] SSRF in Rendertron

## Summary
Severity: Medium
Advisory: GHSA-xr9h-9m79-x29g
CVE: CVE-2020-8902
CWE: CWE-918
Ecosystem: npm
Published: 2021-03-01
Source: https://github.com/advisories/GHSA-xr9h-9m79-x29g
Type: github-advisory

## Affected
- npm: `rendertron` — affected >=0 <3.0.0

## Details
Rendertron versions prior to 3.0.0 are are susceptible to a Server-Side Request Forgery (SSRF) attack. An attacker can use a specially crafted webpage to force a rendertron headless chrome process to render internal sites it has access to, and display it as a screenshot. Suggested mitigations are to upgrade your rendertron to version 3.0.0, or, if you cannot update, to secure the infrastructure to limit the headless chrome's access to your internal domain.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8902
- https://github.com/GoogleChrome/rendertron/releases/tag/3.0.0
- https://www.npmjs.com/package/rendertron
