# [H] Flowise Authentication Bypass vulnerability

## Summary
Severity: High
Advisory: GHSA-2q4w-x8h2-2fvh
CVE: CVE-2024-8181
CWE: CWE-285, CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-08-27
Source: https://github.com/advisories/GHSA-2q4w-x8h2-2fvh
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0

## Details
An Authentication Bypass vulnerability exists in Flowise version 1.8.2. This could allow a remote, unauthenticated attacker to access API endpoints as an administrator and allow them to access restricted functionality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8181
- https://github.com/FlowiseAI/Flowise
- https://tenable.com/security/research/tra-2024-22-0
- https://tenable.com/security/research/tra-2024-33
