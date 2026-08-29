# Q3737: vault-accrue via call-ststx-ratio: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015), controlling whether the ratio is fetched before or after other state changes in the block, drive `vault-accrue` (mainnet/contracts/market/v0-4-market.clar:189) — which dispatches accrual to one of six vaults by asset id — to record a repayment larger than the value actually delivered, breaking the invariant that `assets` never exceeds the underlying the vault actually holds, and cause protocol insolvency?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:189` -> `vault-accrue`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: whether the ratio is fetched before or after other state changes in the block
- Exploit idea: `vault-accrue` dispatches accrual to one of six vaults by asset id. Reach it through `call-ststx-ratio` and record a repayment larger than the value actually delivered.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `call-ststx-ratio` call, then the attacker-shaped one with whether the ratio is fetched before or after other state changes in the block, and assert the attacker's net token balance change is zero or negative.
