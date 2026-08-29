# Q2198: lookup via liquidate: have the same quantity scaled twice by two contracts that 

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `collateral-receiver`, can an unprivileged attacker make `lookup` (mainnet/contracts/registry/v0-assets.clar:139) have the same quantity scaled twice by two contracts that round differently? `lookup` returns the registry record, including the `decimals` captured once at registration, so the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:139` -> `lookup`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `lookup` returns the registry record, including the `decimals` captured once at registration. Reach it through `liquidate` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with `collateral-receiver` varied, and assert that the value `lookup` returns is identical in both runs; a divergence confirms the finding.
