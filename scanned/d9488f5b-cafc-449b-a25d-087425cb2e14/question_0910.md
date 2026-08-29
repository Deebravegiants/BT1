# Q0910: get-full-position via collateral-remove-redeem: mint shares whose backing was never received

## Question
Entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) while controlling remaining zToken collateral whose price moves with the redeem, can an unprivileged attacker make `get-full-position` (mainnet/contracts/market/v0-4-market.clar:470) mint shares whose backing was never received? `get-full-position` returns all collateral rows regardless of the enabled bitmap, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:470` -> `get-full-position`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: remaining zToken collateral whose price moves with the redeem
- Exploit idea: `get-full-position` returns all collateral rows regardless of the enabled bitmap. Reach it through `collateral-remove-redeem` and mint shares whose backing was never received.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `collateral-remove-redeem` with remaining zToken collateral whose price moves with the redeem, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
