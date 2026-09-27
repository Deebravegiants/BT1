# [H] @hulumi/policies: Stack-wide evidence bypassed Cloudflare and deployment-governance guardrails

## Summary
Severity: High
Advisory: GHSA-59f3-7227-wmh4
CWE: CWE-693
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-59f3-7227-wmh4
Type: github-advisory

## Affected
- npm: `@hulumi/policies` — affected >=0 <1.3.2

## Details
Impact: @hulumi/policies versions before 1.3.2 used stack-wide evidence shortcuts in several Cloudflare and deployment-governance validators. Unrelated compliant-looking evidence could suppress violations for different zones, hostnames, origins, or repositories in the same stack.

Patched in 1.3.2: validators now correlate evidence to the specific protected resource and include regression coverage for unrelated-evidence bypasses.

Remediation: upgrade @hulumi/policies to 1.3.2 or later.

## References
- https://github.com/kerberosmansour/hulumi/security/advisories/GHSA-59f3-7227-wmh4
- https://github.com/kerberosmansour/hulumi
