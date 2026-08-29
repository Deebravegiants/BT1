# Q0610: mask-update via liquidate-multi: mint shares whose backing was never received

## Question
Entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) while controlling how many entries share one price snapshot (price-feeds is passed as none), can an unprivileged attacker make `mask-update` (mainnet/contracts/market/v0-market-vault.clar:94) mint shares whose backing was never received? `mask-update` sets or clears one bit, clearing only when the row reaches exactly zero, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:94` -> `mask-update`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: how many entries share one price snapshot (price-feeds is passed as none)
- Exploit idea: `mask-update` sets or clears one bit, clearing only when the row reaches exactly zero. Reach it through `liquidate-multi` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `liquidate-multi` with how many entries share one price snapshot (price-feeds is passed as none), and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
