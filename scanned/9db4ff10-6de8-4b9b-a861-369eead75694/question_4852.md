# Q4852: get-notional-evaluation via liquidate: mint shares whose backing was never received

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `debt-amount` reach `get-notional-evaluation` (mainnet/contracts/market/v0-4-market.clar:514) in a state where it mint shares whose backing was never received? Given that it folds over the ENABLED asset list, so a position row whose asset is absent from that list contributes nothing to either total, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:514` -> `get-notional-evaluation`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `debt-amount`
- Exploit idea: `get-notional-evaluation` folds over the ENABLED asset list, so a position row whose asset is absent from that list contributes nothing to either total. Reach it through `liquidate` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `liquidate` with `debt-amount`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
