# Q2430: vault-accrue via collateral-add: have the same quantity scaled twice by two contracts that 

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling `amount`, can an unprivileged attacker make `vault-accrue` (mainnet/contracts/market/v0-4-market.clar:189) have the same quantity scaled twice by two contracts that round differently? `vault-accrue` dispatches accrual to one of six vaults by asset id, so the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:189` -> `vault-accrue`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `vault-accrue` dispatches accrual to one of six vaults by asset id. Reach it through `collateral-add` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz `amount` across its boundary values through `collateral-add` in simnet and assert `vault-accrue` never returns a value that breaks the invariant.
