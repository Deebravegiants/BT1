# [H] Babylon's malformed vote extensions are not rejected

## Summary
Severity: High
Advisory: GHSA-2fcv-qww3-9v6h
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H (CVSS_V4)
Published: 2025-11-24
Source: https://github.com/advisories/GHSA-2fcv-qww3-9v6h
Type: github-advisory

## Affected
- Go: `github.com/babylonlabs-io/babylon/v4` — affected >=0 <4.1.0

## Details
### Summary

Adversarial validators can send large vote extensions by using non-existing protobuf tags. This will result in the rejection of the subsequent block proposal. Eventually, all block proposals will be rejected by all validators.

### Impact

A small group of adversarial validators can cause a chain halt.

## References
- https://github.com/babylonlabs-io/babylon/security/advisories/GHSA-2fcv-qww3-9v6h
- https://github.com/babylonlabs-io/babylon/pull/1873/commits/86f38abd2dca5a656195a9954bb569a08d662e2b
- https://github.com/babylonlabs-io/babylon
- https://github.com/babylonlabs-io/babylon/releases/tag/v4.1.0
