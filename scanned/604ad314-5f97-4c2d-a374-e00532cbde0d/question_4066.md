# Q4066: next-index via call-ststx-ratio: destroy value through a truncation the opposite operation 

## Question
Entering through `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015) while controlling whether the ratio is fetched before or after other state changes in the block, can an unprivileged attacker make `next-index` (mainnet/contracts/vault/v0-vault-stx.clar:379) destroy value through a truncation the opposite operation does not restore? `next-index` returns the stale `index` unchanged when the accrue pause state is set, instead of reverting, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:379` -> `next-index`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: whether the ratio is fetched before or after other state changes in the block
- Exploit idea: `next-index` returns the stale `index` unchanged when the accrue pause state is set, instead of reverting. Reach it through `call-ststx-ratio` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `call-ststx-ratio` with whether the ratio is fetched before or after other state changes in the block, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
