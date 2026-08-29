# Q3829: resolve-or-create via transfer: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752), controlling the destination principal, including the market, the market-vault or the treasury, drive `resolve-or-create` (mainnet/contracts/market/v0-market-vault.clar:143) — which allocates a user id through `increment` for whatever principal the market names — to record a repayment larger than the value actually delivered, breaking the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:143` -> `resolve-or-create`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the destination principal, including the market, the market-vault or the treasury
- Exploit idea: `resolve-or-create` allocates a user id through `increment` for whatever principal the market names. Reach it through `transfer` and record a repayment larger than the value actually delivered.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `transfer` with the destination principal, including the market, the market-vault or the treasury, then read `resolve-or-create` state before and after in the same block and assert the two sides of the invariant are equal.
