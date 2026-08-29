# Q5008: socialize-debt via repay: record a repayment larger than the value actually delivere

## Question
Does `repay` (mainnet/contracts/market/v0-4-market.clar:1316) let an unprivileged attacker who controls `amount`, including far above the real debt (the capping path) reach `socialize-debt` (mainnet/contracts/vault/v0-vault-stx.clar:944) in a state where it record a repayment larger than the value actually delivered? Given that it writes down `lindex` by one ratio while reducing `assets` by a completely different `principal-reduction`, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:944` -> `socialize-debt`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `amount`, including far above the real debt (the capping path)
- Exploit idea: `socialize-debt` writes down `lindex` by one ratio while reducing `assets` by a completely different `principal-reduction`. Reach it through `repay` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `repay` with `amount`, including far above the real debt (the capping path), and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
