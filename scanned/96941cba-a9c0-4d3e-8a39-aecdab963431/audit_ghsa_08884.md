# [H] @hulumi/policies: HULUMI-H1 SecureBucket parent spoof bypass

## Summary
Severity: High
Advisory: GHSA-g43v-9x7q-83pq
CWE: CWE-284
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-g43v-9x7q-83pq
Type: github-advisory

## Affected
- npm: `@hulumi/policies` — affected >=0 <1.3.2

## Details
Impact: @hulumi/policies versions before 1.3.2 could accept spoofed SecureBucket parent evidence for HULUMI-H1, allowing policy evaluation to miss an unsafe bucket shape.

Patched in 1.3.2: the validator now correlates evidence to the expected component/resource relationship and includes regression coverage.

Remediation: upgrade @hulumi/policies to 1.3.2 or later.

## References
- https://github.com/kerberosmansour/hulumi/security/advisories/GHSA-g43v-9x7q-83pq
- https://github.com/kerberosmansour/hulumi
