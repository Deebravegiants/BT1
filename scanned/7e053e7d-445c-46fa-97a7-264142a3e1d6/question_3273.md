# Q3273: mask-to-list-collateral via collateral-remove-redeem: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), controlling `amount` used for BOTH the collateral removal and the share redemption, drive `mask-to-list-collateral` (mainnet/contracts/market/v0-4-market.clar:449) — which expands a mask to a list of ids over ITER-UINT-64 — to record a repayment larger than the value actually delivered, breaking the invariant that `assets` never exceeds the underlying the vault actually holds, and cause permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:449` -> `mask-to-list-collateral`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `amount` used for BOTH the collateral removal and the share redemption
- Exploit idea: `mask-to-list-collateral` expands a mask to a list of ids over ITER-UINT-64. Reach it through `collateral-remove-redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `mask-to-list-collateral` touches, run `collateral-remove-redeem` with `amount` used for BOTH the collateral removal and the share redemption, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
