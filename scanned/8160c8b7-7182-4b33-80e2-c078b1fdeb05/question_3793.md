# Q3793: vault-accrue via redeem: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797), controlling `amount` of shares burned, drive `vault-accrue` (mainnet/contracts/market/v0-4-market.clar:189) — which dispatches accrual to one of six vaults by asset id — to record a repayment larger than the value actually delivered, breaking the invariant that `assets` never exceeds the underlying the vault actually holds, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:189` -> `vault-accrue`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `amount` of shares burned
- Exploit idea: `vault-accrue` dispatches accrual to one of six vaults by asset id. Reach it through `redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `redeem` with `amount` of shares burned, then read `vault-accrue` state before and after in the same block and assert the two sides of the invariant are equal.
