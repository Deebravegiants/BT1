# Q5320: find-collateral-amount via liquidate-redeem: record a repayment larger than the value actually delivere

## Question
Does `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) let an unprivileged attacker who controls the seized zToken amount that is immediately redeemed reach `find-collateral-amount` (mainnet/contracts/market/v0-4-market.clar:609) in a state where it record a repayment larger than the value actually delivered? Given that it returns u0 for an absent asset, making a missing row indistinguishable from a zero holding, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:609` -> `find-collateral-amount`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the seized zToken amount that is immediately redeemed
- Exploit idea: `find-collateral-amount` returns u0 for an absent asset, making a missing row indistinguishable from a zero holding. Reach it through `liquidate-redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `liquidate-redeem` with the seized zToken amount that is immediately redeemed, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
