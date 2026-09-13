# [H] @hulumi/drift: Orphan reconciler accepted externally supplied execute plans

## Summary
Severity: High
Advisory: GHSA-2ffm-hxrq-qqmm
CWE: CWE-345
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-2ffm-hxrq-qqmm
Type: github-advisory

## Affected
- npm: `@hulumi/drift` — affected >=0 <1.3.2

## Details
Impact: @hulumi/drift versions before 1.3.2 could accept externally supplied execute plans without sufficient provenance checks, allowing unsafe reconciliation input to be treated as trusted.

Patched in 1.3.2: execute-plan handling now validates provenance and rejects untrusted plans, with regression coverage.

Remediation: upgrade @hulumi/drift to 1.3.2 or later.

## References
- https://github.com/kerberosmansour/hulumi/security/advisories/GHSA-2ffm-hxrq-qqmm
- https://github.com/kerberosmansour/hulumi
