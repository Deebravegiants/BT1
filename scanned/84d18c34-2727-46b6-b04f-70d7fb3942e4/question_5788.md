# Q5788: send-underlying via transfer: record a repayment larger than the value actually delivere

## Question
Does `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) let an unprivileged attacker who controls the timing relative to a pledge or a liquidation reach `send-underlying` (mainnet/contracts/vault/v0-vault-stx.clar:296) in a state where it record a repayment larger than the value actually delivered? Given that it pushes the underlying under an `as-contract?` post-condition scope, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:296` -> `send-underlying`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the timing relative to a pledge or a liquidation
- Exploit idea: `send-underlying` pushes the underlying under an `as-contract?` post-condition scope. Reach it through `transfer` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `transfer` with the timing relative to a pledge or a liquidation, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
