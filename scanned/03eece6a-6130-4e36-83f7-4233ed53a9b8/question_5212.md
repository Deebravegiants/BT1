# Q5212: total-debt via collateral-remove-redeem: record a repayment larger than the value actually delivere

## Question
Does `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) let an unprivileged attacker who controls `min-underlying` reach `total-debt` (mainnet/contracts/vault/v0-vault-stx.clar:328) in a state where it record a repayment larger than the value actually delivered? Given that it computes cumulative debt from `principal-scaled` and `index`, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:328` -> `total-debt`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `min-underlying`
- Exploit idea: `total-debt` computes cumulative debt from `principal-scaled` and `index`. Reach it through `collateral-remove-redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `collateral-remove-redeem` with `min-underlying`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
