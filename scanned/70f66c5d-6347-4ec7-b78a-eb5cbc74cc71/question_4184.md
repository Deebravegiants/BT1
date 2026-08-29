# Q4184: is-liquidation-paused via liquidate: mint shares whose backing was never received

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls the `price-feeds` buffers and their ordering reach `is-liquidation-paused` (mainnet/contracts/market/v0-4-market.clar:691) in a state where it mint shares whose backing was never received? Given that it returns true if the manual pause, the GLOBAL grace entry, OR the per-asset grace entry is live, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:691` -> `is-liquidation-paused`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers and their ordering
- Exploit idea: `is-liquidation-paused` returns true if the manual pause, the GLOBAL grace entry, OR the per-asset grace entry is live. Reach it through `liquidate` and mint shares whose backing was never received.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with the `price-feeds` buffers and their ordering varied, and assert that the value `is-liquidation-paused` returns is identical in both runs; a divergence confirms the finding.
