# Q3725: create via collateral-remove-redeem: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), controlling `receiver` for the underlying leg, drive `create` (mainnet/contracts/market/v0-market-vault.clar:150) — which binds a principal to a fresh numeric id — to record a repayment larger than the value actually delivered, breaking the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal, and cause protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:150` -> `create`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `receiver` for the underlying leg
- Exploit idea: `create` binds a principal to a fresh numeric id. Reach it through `collateral-remove-redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `collateral-remove-redeem` call, then the attacker-shaped one with `receiver` for the underlying leg, and assert the attacker's net token balance change is zero or negative.
