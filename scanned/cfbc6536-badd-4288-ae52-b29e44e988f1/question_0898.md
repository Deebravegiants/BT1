# Q0898: accrue-user-collateral via liquidate: mint shares whose backing was never received

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `collateral-receiver`, can an unprivileged attacker make `accrue-user-collateral` (mainnet/contracts/market/v0-4-market.clar:270) mint shares whose backing was never received? `accrue-user-collateral` accrues only rows that `is-ztoken` recognises, skipping everything else, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:270` -> `accrue-user-collateral`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `accrue-user-collateral` accrues only rows that `is-ztoken` recognises, skipping everything else. Reach it through `liquidate` and mint shares whose backing was never received.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `liquidate` with `collateral-receiver`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
