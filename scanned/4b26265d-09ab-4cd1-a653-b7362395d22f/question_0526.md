# Q0526: scale-debt-for-liquidation via liquidate-multi: mint shares whose backing was never received

## Question
Entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) while controlling how many entries share one price snapshot (price-feeds is passed as none), can an unprivileged attacker make `scale-debt-for-liquidation` (mainnet/contracts/market/v0-4-market.clar:858) mint shares whose backing was never received? `scale-debt-for-liquidation` re-scales collateral by `scaled-to-remove / scaled-debt` after the debt was already capped, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:858` -> `scale-debt-for-liquidation`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: how many entries share one price snapshot (price-feeds is passed as none)
- Exploit idea: `scale-debt-for-liquidation` re-scales collateral by `scaled-to-remove / scaled-debt` after the debt was already capped. Reach it through `liquidate-multi` and mint shares whose backing was never received.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `liquidate-multi` with how many entries share one price snapshot (price-feeds is passed as none), and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
