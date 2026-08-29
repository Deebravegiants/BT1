# Q4006: accrue-user-debts via accrue: destroy value through a truncation the opposite operation 

## Question
Entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) while controlling the utilization the rate is interpolated at, can an unprivileged attacker make `accrue-user-debts` (mainnet/contracts/market/v0-4-market.clar:259) destroy value through a truncation the opposite operation does not restore? `accrue-user-debts` folds accrual over the position's debt list only, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:259` -> `accrue-user-debts`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the utilization the rate is interpolated at
- Exploit idea: `accrue-user-debts` folds accrual over the position's debt list only. Reach it through `accrue` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `accrue` with the utilization the rate is interpolated at, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
