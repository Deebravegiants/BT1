# Q3149: user-safe-mask via supply-collateral-add: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), controlling `min-shares` (the only slippage bound on the deposit leg), drive `user-safe-mask` (mainnet/contracts/market/v0-4-market.clar:428) — which ANDs the user's collateral bits against the enabled bitmap but keeps ALL debt bits unfiltered — to record a repayment larger than the value actually delivered, breaking the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal, and cause permanent freezing of unclaimed yield?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:428` -> `user-safe-mask`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `min-shares` (the only slippage bound on the deposit leg)
- Exploit idea: `user-safe-mask` ANDs the user's collateral bits against the enabled bitmap but keeps ALL debt bits unfiltered. Reach it through `supply-collateral-add` and record a repayment larger than the value actually delivered.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Run the baseline `supply-collateral-add` call, then the attacker-shaped one with `min-shares` (the only slippage bound on the deposit leg), and assert the attacker's net token balance change is zero or negative.
