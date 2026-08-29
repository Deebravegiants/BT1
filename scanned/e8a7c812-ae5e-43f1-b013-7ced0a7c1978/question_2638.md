# Q2638: convert-to-assets-preview via collateral-remove-redeem: have the same quantity scaled twice by two contracts that 

## Question
Entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) while controlling remaining zToken collateral whose price moves with the redeem, can an unprivileged attacker make `convert-to-assets-preview` (mainnet/contracts/vault/v0-vault-stx.clar:317) have the same quantity scaled twice by two contracts that round differently? `convert-to-assets-preview` prices a redemption against `total-assets-preview` and `total-supply-preview`, so the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:317` -> `convert-to-assets-preview`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: remaining zToken collateral whose price moves with the redeem
- Exploit idea: `convert-to-assets-preview` prices a redemption against `total-assets-preview` and `total-supply-preview`. Reach it through `collateral-remove-redeem` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `collateral-remove-redeem` with remaining zToken collateral whose price moves with the redeem, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
