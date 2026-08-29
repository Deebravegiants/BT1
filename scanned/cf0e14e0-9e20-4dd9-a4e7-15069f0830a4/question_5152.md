# Q5152: accrue-debt-asset via liquidate-redeem: record a repayment larger than the value actually delivere

## Question
Does `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604) let an unprivileged attacker who controls the seized zToken amount that is immediately redeemed reach `accrue-debt-asset` (mainnet/contracts/market/v0-4-market.clar:262) in a state where it record a repayment larger than the value actually delivered? Given that it calls `accrue-and-cache` with `unwrap-panic` inside a fold whose accumulator ignores the result, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:262` -> `accrue-debt-asset`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the seized zToken amount that is immediately redeemed
- Exploit idea: `accrue-debt-asset` calls `accrue-and-cache` with `unwrap-panic` inside a fold whose accumulator ignores the result. Reach it through `liquidate-redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `liquidate-redeem` with the seized zToken amount that is immediately redeemed, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
