# [?] [stableswap]: Cap number of assets and post-scaled asset amounts to ensure pools never overflow (#3055)

## Summary
Severity: Unknown
Chain: Osmosis
Component: osmosis-labs/osmosis
Published: 2022-10-24
Source: https://github.com/osmosis-labs/osmosis/commit/ced84c1c8a656c66b4e54baf2a271d456b25a119
Type: security-commit

## Details
[stableswap]: Cap number of assets and post-scaled asset amounts to ensure pools never overflow (#3055)

* add tests for 10-asset pools with 10B per asset

* add max post-scaled asset check and create pool tests

* add sanity tests for new swap guardrails

* move max scaled asset amt to constant

* add join-pool-internal tests for new functionality
