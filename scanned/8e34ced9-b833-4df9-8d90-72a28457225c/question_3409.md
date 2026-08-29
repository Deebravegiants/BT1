# Q3409: vault-accrue via collateral-add: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), controlling the position's existing collateral and debt composition, drive `vault-accrue` (mainnet/contracts/market/v0-4-market.clar:189) — which dispatches accrual to one of six vaults by asset id — to record a repayment larger than the value actually delivered, breaking the invariant that `assets` never exceeds the underlying the vault actually holds, and cause theft of unclaimed yield?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:189` -> `vault-accrue`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the position's existing collateral and debt composition
- Exploit idea: `vault-accrue` dispatches accrual to one of six vaults by asset id. Reach it through `collateral-add` and record a repayment larger than the value actually delivered.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-add` with the position's existing collateral and debt composition, then read `vault-accrue` state before and after in the same block and assert the two sides of the invariant are equal.
