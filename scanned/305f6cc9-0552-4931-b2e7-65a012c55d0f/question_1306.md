# Q1306: interest-rate via supply-collateral-add: record a repayment larger than the value actually delivere

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling `min-shares` (the only slippage bound on the deposit leg), can an unprivileged attacker make `interest-rate` (mainnet/contracts/vault/v0-vault-stx.clar:371) record a repayment larger than the value actually delivered? `interest-rate` interpolates the packed curve at the current utilization, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:371` -> `interest-rate`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `min-shares` (the only slippage bound on the deposit leg)
- Exploit idea: `interest-rate` interpolates the packed curve at the current utilization. Reach it through `supply-collateral-add` and record a repayment larger than the value actually delivered.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `supply-collateral-add` with `min-shares` (the only slippage bound on the deposit leg), and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
