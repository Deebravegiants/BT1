# Q1954: vault-system-repay via liquidate: record a repayment larger than the value actually delivere

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling which collateral and debt asset pair is targeted, can an unprivileged attacker make `vault-system-repay` (mainnet/contracts/market/v0-4-market.clar:207) record a repayment larger than the value actually delivered? `vault-system-repay` routes a repayment to one of six vaults by asset id, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:207` -> `vault-system-repay`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: which collateral and debt asset pair is targeted
- Exploit idea: `vault-system-repay` routes a repayment to one of six vaults by asset id. Reach it through `liquidate` and record a repayment larger than the value actually delivered.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `liquidate` with which collateral and debt asset pair is targeted, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
