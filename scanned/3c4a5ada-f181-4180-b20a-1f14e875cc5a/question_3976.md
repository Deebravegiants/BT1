# Q3976: next-index via redeem: mint shares whose backing was never received

## Question
Does `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) let an unprivileged attacker who controls the gap between the `assets` var and the real balance reach `next-index` (mainnet/contracts/vault/v0-vault-stx.clar:379) in a state where it mint shares whose backing was never received? Given that it returns the stale `index` unchanged when the accrue pause state is set, instead of reverting, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:379` -> `next-index`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the gap between the `assets` var and the real balance
- Exploit idea: `next-index` returns the stale `index` unchanged when the accrue pause state is set, instead of reverting. Reach it through `redeem` and mint shares whose backing was never received.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `redeem` with the gap between the `assets` var and the real balance, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
