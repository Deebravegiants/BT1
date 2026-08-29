# Q3477: resolve-price-feed via liquidate-redeem: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), controlling the borrower targeted, drive `resolve-price-feed` (mainnet/contracts/market/v0-4-market.clar:332) — which dispatches on a 1-byte type to `resolve-pyth` or `resolve-dia`, erroring otherwise — to record a repayment larger than the value actually delivered, breaking the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:332` -> `resolve-price-feed`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the borrower targeted
- Exploit idea: `resolve-price-feed` dispatches on a 1-byte type to `resolve-pyth` or `resolve-dia`, erroring otherwise. Reach it through `liquidate-redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `resolve-price-feed` touches, run `liquidate-redeem` with the borrower targeted, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
