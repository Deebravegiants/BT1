# [H] Babylon vulnerable to chain half when transaction has fees different than `ubbn`

## Summary
Severity: High
Advisory: GHSA-56j4-446m-qrf6
CWE: CWE-755
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-06-30
Source: https://github.com/advisories/GHSA-56j4-446m-qrf6
Type: github-advisory

## Affected
- Go: `github.com/babylonlabs-io/babylon/v2` — affected >=0 <2.2.0
- Go: `github.com/babylonlabs-io/babylon` — affected >=0

## Details
### Summary

Sending transactions with fees different than native Babylon genesis denom (`ubbn`) leads to chain halt.

### Impact

Denial of Service - Due to panic in the `x/distribution` module `BeginBlocker` triggered by a error when sending fees  from `feeCollector` to `x/distribution` module - https://github.com/cosmos/cosmos-sdk/blob/main/x/distribution/keeper/allocation.go#L28 Babylon Genesis will halt

## References
- https://github.com/babylonlabs-io/babylon/security/advisories/GHSA-56j4-446m-qrf6
- https://github.com/babylonlabs-io/babylon/commit/fe67aebd5216e7d3afa1d7dee2a3f82e548556f3
- https://github.com/babylonlabs-io/babylon
- https://github.com/cosmos/cosmos-sdk/blob/main/x/distribution/keeper/allocation.go#L28
