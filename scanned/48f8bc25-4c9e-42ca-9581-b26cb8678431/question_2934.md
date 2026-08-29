# Q2934: calc-cumulative-debt via collateral-remove-redeem: have the same quantity scaled twice by two contracts that 

## Question
Entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) while controlling `amount` used for BOTH the collateral removal and the share redemption, can an unprivileged attacker make `calc-cumulative-debt` (mainnet/contracts/vault/v0-vault-stx.clar:180) have the same quantity scaled twice by two contracts that round differently? `calc-cumulative-debt` multiplies scaled principal by an index, so the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:180` -> `calc-cumulative-debt`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `amount` used for BOTH the collateral removal and the share redemption
- Exploit idea: `calc-cumulative-debt` multiplies scaled principal by an index. Reach it through `collateral-remove-redeem` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `amount` used for BOTH the collateral removal and the share redemption across its boundary values through `collateral-remove-redeem` in simnet and assert `calc-cumulative-debt` never returns a value that breaks the invariant.
