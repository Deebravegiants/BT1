# Q3049: calc-index-next via repay: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316), controlling whether the repaid asset is in the accrued debt list, drive `calc-index-next` (mainnet/contracts/vault/v0-vault-stx.clar:183) — which applies a multiplier to the current index — to record a repayment larger than the value actually delivered, breaking the invariant that `assets` never exceeds the underlying the vault actually holds, and cause theft of unclaimed yield?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:183` -> `calc-index-next`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: whether the repaid asset is in the accrued debt list
- Exploit idea: `calc-index-next` applies a multiplier to the current index. Reach it through `repay` and record a repayment larger than the value actually delivered.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: In `local-testing/tests` on a local fork, drive `repay` with whether the repaid asset is in the accrued debt list, then read `calc-index-next` state before and after in the same block and assert the two sides of the invariant are equal.
