# Q0040: find-superset via liquidate: destroy value through a truncation the opposite operation 

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `collateral-receiver` reach `find-superset` (mainnet/contracts/registry/v0-egroup.clar:262) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it returns the FIRST mask that is a superset, walking buckets in population order rather than finding the tightest, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:262` -> `find-superset`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `find-superset` returns the FIRST mask that is a superset, walking buckets in population order rather than finding the tightest. Reach it through `liquidate` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `liquidate` with `collateral-receiver`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
