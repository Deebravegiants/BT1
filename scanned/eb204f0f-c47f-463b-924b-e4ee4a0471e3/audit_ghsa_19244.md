# [H] Babylon Integer Overflow in Distribution Module CumulativeRewardRatio Calculation Leading to Chain Halt

## Summary
Severity: High
Advisory: GHSA-869w-47c6-fq8q
CWE: CWE-190, CWE-770
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-05-15
Source: https://github.com/advisories/GHSA-869w-47c6-fq8q
Type: github-advisory

## Affected
- Go: `github.com/babylonlabs-io/babylon` — affected >=0 <1.1.0

## Details
### Summary
Minting large amount of tokens through ibc transfer and then depositing them in validator rewards pool (via `DepositValidatorRewardsPool` message) can lead to integer overflow panic when calculating `cumulative_reward_ratio` for the validator.

This calculation happens in `x/epoching` module `EndBlocker`, thus the panic will halt the chain.

### Impact

Denial of Service - Due to panic in the `EndBlocker` Babylon Genesis will halt

## References
- https://github.com/babylonlabs-io/babylon/security/advisories/GHSA-869w-47c6-fq8q
- https://github.com/babylonlabs-io/babylon/commit/f0a29d60f206268b56992fa50f38a48077eb4f59
- https://github.com/babylonlabs-io/babylon
- https://pkg.go.dev/vuln/GO-2025-3687
