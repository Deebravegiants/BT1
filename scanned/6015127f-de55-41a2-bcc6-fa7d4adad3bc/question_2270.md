# Q2270: resolve-interpolation-points via borrow: have the same quantity scaled twice by two contracts that 

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling the `price-feeds` buffers, can an unprivileged attacker make `resolve-interpolation-points` (mainnet/contracts/vault/v0-vault-stx.clar:205) have the same quantity scaled twice by two contracts that round differently? `resolve-interpolation-points` selects the bracketing curve points for a utilization, so the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:205` -> `resolve-interpolation-points`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `resolve-interpolation-points` selects the bracketing curve points for a utilization. Reach it through `borrow` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with the `price-feeds` buffers varied, and assert that the value `resolve-interpolation-points` returns is identical in both runs; a divergence confirms the finding.
