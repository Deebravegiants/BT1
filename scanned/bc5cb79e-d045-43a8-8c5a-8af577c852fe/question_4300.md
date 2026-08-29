# Q4300: process-collateral-asset via liquidate: mint shares whose backing was never received

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `debt-amount` reach `process-collateral-asset` (mainnet/contracts/market/v0-4-market.clar:789) in a state where it mint shares whose backing was never received? Given that it computes expected collateral, then caps it at the borrower's balance, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:789` -> `process-collateral-asset`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `debt-amount`
- Exploit idea: `process-collateral-asset` computes expected collateral, then caps it at the borrower's balance. Reach it through `liquidate` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `liquidate` with `debt-amount`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
