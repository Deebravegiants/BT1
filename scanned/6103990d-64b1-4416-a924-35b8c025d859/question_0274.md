# Q0274: mask-shift-combine via liquidate: mint shares whose backing was never received

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `collateral-receiver`, can an unprivileged attacker make `mask-shift-combine` (mainnet/contracts/market/v0-4-market.clar:422) mint shares whose backing was never received? `mask-shift-combine` folds the 128-bit mask down by shifting the debt half by DEBT-OFFSET and OR-ing it onto the collateral half, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:422` -> `mask-shift-combine`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `mask-shift-combine` folds the 128-bit mask down by shifting the debt half by DEBT-OFFSET and OR-ing it onto the collateral half. Reach it through `liquidate` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `liquidate` with `collateral-receiver`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
