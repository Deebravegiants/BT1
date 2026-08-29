# Q5986: calc-index-next via repay: credit one side of an accounting pair without the other

## Question
Entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316) while controlling whether the repaid asset is in the accrued debt list, can an unprivileged attacker make `calc-index-next` (mainnet/contracts/vault/v0-vault-stx.clar:183) credit one side of an accounting pair without the other? `calc-index-next` applies a multiplier to the current index, so the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:183` -> `calc-index-next`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: whether the repaid asset is in the accrued debt list
- Exploit idea: `calc-index-next` applies a multiplier to the current index. Reach it through `repay` and credit one side of an accounting pair without the other.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `repay` with whether the repaid asset is in the accrued debt list, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
