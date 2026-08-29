# Q3561: subset via repay: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316), controlling whether the repaid asset is in the accrued debt list, drive `subset` (mainnet/contracts/market/v0-market-vault.clar:100) — which tests bitmask containment — to record a repayment larger than the value actually delivered, breaking the invariant that `assets` never exceeds the underlying the vault actually holds, and cause permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:100` -> `subset`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: whether the repaid asset is in the accrued debt list
- Exploit idea: `subset` tests bitmask containment. Reach it through `repay` and record a repayment larger than the value actually delivered.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `subset` touches, run `repay` with whether the repaid asset is in the accrued debt list, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
