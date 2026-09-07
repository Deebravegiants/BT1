# [M] Babylon's BIP322 signature implementation is not fully compliant to the spec

## Summary
Severity: Medium
Advisory: GHSA-xq4h-wqm2-668w
CWE: CWE-347
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-11-24
Source: https://github.com/advisories/GHSA-xq4h-wqm2-668w
Type: github-advisory

## Affected
- Go: `github.com/babylonlabs-io/babylon/v4` — affected >=0 <4.1.0

## Details
### Summary

The BIP-322 signature verification does not enforce the SIGHASH value to be SIGHASH_ALL, and therefore is not strictly following the [spec](https://bips.dev/322/).

### Impact

Non-compliant BIP-322 signatures in proof of possessions can be accepted by the chain.

## References
- https://github.com/babylonlabs-io/babylon/security/advisories/GHSA-xq4h-wqm2-668w
- https://github.com/babylonlabs-io/babylon/commit/6e8bdd328a47343fcd7ad98d1b0c7267860b019a
- https://bips.dev/322
- https://github.com/babylonlabs-io/babylon
