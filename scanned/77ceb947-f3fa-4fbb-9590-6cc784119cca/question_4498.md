# Q4498: next-liquidity-index via supply-collateral-add: destroy value through a truncation the opposite operation 

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling `min-shares` (the only slippage bound on the deposit leg), can an unprivileged attacker make `next-liquidity-index` (mainnet/contracts/vault/v0-vault-stx.clar:392) destroy value through a truncation the opposite operation does not restore? `next-liquidity-index` rounds the liquidity multiplier down while `next-index` rounds the debt multiplier up over the same interval, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:392` -> `next-liquidity-index`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `min-shares` (the only slippage bound on the deposit leg)
- Exploit idea: `next-liquidity-index` rounds the liquidity multiplier down while `next-index` rounds the debt multiplier up over the same interval. Reach it through `supply-collateral-add` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `supply-collateral-add` with `min-shares` (the only slippage bound on the deposit leg), and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
