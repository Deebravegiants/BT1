# Q3353: vault-accrue via liquidate-redeem: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), controlling the borrower targeted, drive `vault-accrue` (mainnet/contracts/market/v0-4-market.clar:189) — which dispatches accrual to one of six vaults by asset id — to record a repayment larger than the value actually delivered, breaking the invariant that `assets` never exceeds the underlying the vault actually holds, and cause protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:189` -> `vault-accrue`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the borrower targeted
- Exploit idea: `vault-accrue` dispatches accrual to one of six vaults by asset id. Reach it through `liquidate-redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `liquidate-redeem` call, then the attacker-shaped one with the borrower targeted, and assert the attacker's net token balance change is zero or negative.
