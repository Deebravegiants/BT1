# [?] Merge pull request #16 from opentensor/security/ghsa-2026-012-staking-coldkey-index-unbounded-growth

## Summary
Severity: Unknown
Chain: Bittensor
Component: opentensor/subtensor
Published: 2026-06-13
Source: https://github.com/RaoFoundation/subtensor/commit/a0944973e22f8d61904bad186e3346e221f19a97
Type: security-commit

## Details
Merge pull request #16 from opentensor/security/ghsa-2026-012-staking-coldkey-index-unbounded-growth

StakingColdkeysByIndex / NumStakingColdkeys grow monotonically and are never pruned on full unstake or coldkey swap
