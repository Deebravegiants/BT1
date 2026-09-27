# [H] @hulumi/policies: CIS 1.16 admin policy bypass for inline and attached IAM policies

## Summary
Severity: High
Advisory: GHSA-4xrh-5m3m-328w
CWE: CWE-269
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-4xrh-5m3m-328w
Type: github-advisory

## Affected
- npm: `@hulumi/policies` — affected >=0 <1.3.2

## Details
Impact: @hulumi/policies versions before 1.3.2 did not fully inspect inline and attached IAM policy evidence for the administrator-policy guardrail, so some admin-equivalent policy paths could pass policy evaluation.

Patched in 1.3.2: the validator inspects the affected policy shapes and includes regression tests.

Remediation: upgrade @hulumi/policies to 1.3.2 or later.

## References
- https://github.com/kerberosmansour/hulumi/security/advisories/GHSA-4xrh-5m3m-328w
- https://github.com/kerberosmansour/hulumi
