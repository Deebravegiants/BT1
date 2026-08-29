# Q5176: mask-update via supply-collateral-add: record a repayment larger than the value actually delivere

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls `amount` reach `mask-update` (mainnet/contracts/market/v0-market-vault.clar:94) in a state where it record a repayment larger than the value actually delivered? Given that it sets or clears one bit, clearing only when the row reaches exactly zero, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:94` -> `mask-update`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `mask-update` sets or clears one bit, clearing only when the row reaches exactly zero. Reach it through `supply-collateral-add` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `supply-collateral-add` with `amount`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
