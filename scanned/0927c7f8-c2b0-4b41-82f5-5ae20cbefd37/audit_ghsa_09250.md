# [M] @hulumi/baseline: CloudTrail selector tampering events were not fully detected

## Summary
Severity: Medium
Advisory: GHSA-gfp8-mp24-5vxg
CWE: CWE-778
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-gfp8-mp24-5vxg
Type: github-advisory

## Affected
- npm: `@hulumi/baseline` — affected >=0 <1.3.2

## Details
Impact: @hulumi/baseline versions before 1.3.2 could miss some CloudTrail event-selector tampering evidence, reducing coverage for changes to audit logging configuration.

Patched in 1.3.2: detection coverage and regression tests were expanded.

Remediation: upgrade @hulumi/baseline to 1.3.2 or later and rerun affected previews/checks.

## References
- https://github.com/kerberosmansour/hulumi/security/advisories/GHSA-gfp8-mp24-5vxg
- https://github.com/kerberosmansour/hulumi
