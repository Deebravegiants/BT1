# [?] Merge pull request #10 from opentensor/security/ghsa-2026-006-weights-pays-no-dispatch-only-ratelimit-flood

## Summary
Severity: Unknown
Chain: Bittensor
Component: opentensor/subtensor
Published: 2026-06-13
Source: https://github.com/RaoFoundation/subtensor/commit/03a79d08e43d6178e6a6d52cfffcfc7b856bf32c
Type: security-commit

## Details
Merge pull request #10 from opentensor/security/ghsa-2026-006-weights-pays-no-dispatch-only-ratelimit-flood

set_weights / commit_weights family is `Pays::No` with the per-neuron rate limit enforced only in the dispatch body, enabling fee-free block-fill flooding
