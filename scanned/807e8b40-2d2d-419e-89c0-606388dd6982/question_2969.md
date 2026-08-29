# Q2969: calc-liq-collateral-repay via liquidate-redeem: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), controlling the borrower targeted, drive `calc-liq-collateral-repay` (mainnet/contracts/market/v0-4-market.clar:728) — which scales the repaid debt by `(+ BPS liq-penalty)` — to record a repayment larger than the value actually delivered, breaking the invariant that `assets` never exceeds the underlying the vault actually holds, and cause permanent freezing of unclaimed yield?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:728` -> `calc-liq-collateral-repay`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the borrower targeted
- Exploit idea: `calc-liq-collateral-repay` scales the repaid debt by `(+ BPS liq-penalty)`. Reach it through `liquidate-redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Run the baseline `liquidate-redeem` call, then the attacker-shaped one with the borrower targeted, and assert the attacker's net token balance change is zero or negative.
