# [H] Babylon vulnerable to chain halt when a message modifies the validator set at the epoch boundary

## Summary
Severity: High
Advisory: GHSA-rj53-j6jw-7f7g
CWE: CWE-754
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H (CVSS_V4)
Published: 2025-07-08
Source: https://github.com/advisories/GHSA-rj53-j6jw-7f7g
Type: github-advisory

## Affected
- Go: `github.com/babylonlabs-io/babylon/v2` — affected >=2.0.0 <2.1.0

## Details
### Summary

Sending a message that modifies the validator set at the epoch boundary halts the chain.

### Impact

Denial of Service - Comos-sdk prevents modifying the validator set from two different modules - https://github.com/cosmos/cosmos-sdk/blob/release/v0.50.x/types/module/module.go#L811. Such an operation leads to panic and chain halt.

### Detailed Post mortem

https://boiling-lake-106.notion.site/2025-06-18-Genesis-mainnet-chain-halt-post-mortem-229f60cc1b5f80b7adf5e3ea0541ea87

## References
- https://github.com/babylonlabs-io/babylon/security/advisories/GHSA-rj53-j6jw-7f7g
- https://github.com/babylonlabs-io/babylon/pull/1244/files
- https://boiling-lake-106.notion.site/2025-06-18-Babylon-Genesis-Chain-Halt-Post-Mortem-229f60cc1b5f80b7adf5e3ea0541ea87
- https://github.com/babylonlabs-io/babylon
- https://github.com/babylonlabs-io/babylon/releases/tag/v2.1.0
