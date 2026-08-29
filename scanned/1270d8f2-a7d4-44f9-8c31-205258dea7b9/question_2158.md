# Q2158: zip via redeem: have the same quantity scaled twice by two contracts that 

## Question
Entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) while controlling the gap between the `assets` var and the real balance, can an unprivileged attacker make `zip` (mainnet/contracts/vault/v0-vault-stx.clar:226) have the same quantity scaled twice by two contracts that round differently? `zip` pairs the utilization and rate point lists element by element, so the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset would fail, yielding theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:226` -> `zip`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the gap between the `assets` var and the real balance
- Exploit idea: `zip` pairs the utilization and rate point lists element by element. Reach it through `redeem` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `redeem` with the gap between the `assets` var and the real balance, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
