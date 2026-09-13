# [C] @hulumi/policies: GitHub OIDC trust policy bypass via AWS set-qualified condition operators

## Summary
Severity: Critical
Advisory: GHSA-q2f7-m237-v562
CWE: CWE-284
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-q2f7-m237-v562
Type: github-advisory

## Affected
- npm: `@hulumi/policies` — affected >=0 <1.3.2

## Details
Impact: @hulumi/policies versions before 1.3.2 only checked exact AWS IAM StringLike/StringEquals condition operator keys in G_OIDC_1. Set-qualified operators such as ForAnyValue:StringLike could hide wildcard GitHub Actions OIDC sub conditions from the mandatory guardrail.

Patched in 1.3.2: the AWS trust-policy inspector now evaluates set-qualified string operators and rejects unsafe GitHub OIDC sub conditions.

Remediation: upgrade @hulumi/policies to 1.3.2 or later.

## References
- https://github.com/kerberosmansour/hulumi/security/advisories/GHSA-q2f7-m237-v562
- https://github.com/kerberosmansour/hulumi
