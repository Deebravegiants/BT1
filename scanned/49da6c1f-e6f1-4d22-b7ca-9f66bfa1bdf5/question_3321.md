# Q3321: process-collateral-asset via liquidate: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), controlling the `price-feeds` buffers and their ordering, drive `process-collateral-asset` (mainnet/contracts/market/v0-4-market.clar:789) — which computes expected collateral, then caps it at the borrower's balance — to record a repayment larger than the value actually delivered, breaking the invariant that `assets` never exceeds the underlying the vault actually holds, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:789` -> `process-collateral-asset`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers and their ordering
- Exploit idea: `process-collateral-asset` computes expected collateral, then caps it at the borrower's balance. Reach it through `liquidate` and record a repayment larger than the value actually delivered.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `process-collateral-asset` touches, run `liquidate` with the `price-feeds` buffers and their ordering, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
