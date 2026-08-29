# Q4180: resolve-price-feed via liquidate: mint shares whose backing was never received

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `debt-amount` reach `resolve-price-feed` (mainnet/contracts/market/v0-4-market.clar:332) in a state where it mint shares whose backing was never received? Given that it dispatches on a 1-byte type to `resolve-pyth` or `resolve-dia`, erroring otherwise, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:332` -> `resolve-price-feed`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `debt-amount`
- Exploit idea: `resolve-price-feed` dispatches on a 1-byte type to `resolve-pyth` or `resolve-dia`, erroring otherwise. Reach it through `liquidate` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `liquidate` with `debt-amount`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
