# Q2070: calc-index-next via repay: have the same quantity scaled twice by two contracts that 

## Question
Entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316) while controlling whether the repaid asset is in the accrued debt list, can an unprivileged attacker make `calc-index-next` (mainnet/contracts/vault/v0-vault-stx.clar:183) have the same quantity scaled twice by two contracts that round differently? `calc-index-next` applies a multiplier to the current index, so the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset would fail, yielding temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:183` -> `calc-index-next`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: whether the repaid asset is in the accrued debt list
- Exploit idea: `calc-index-next` applies a multiplier to the current index. Reach it through `repay` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz whether the repaid asset is in the accrued debt list across its boundary values through `repay` in simnet and assert `calc-index-next` never returns a value that breaks the invariant.
