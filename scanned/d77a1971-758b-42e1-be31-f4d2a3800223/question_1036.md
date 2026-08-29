# Q1036: find-superset via borrow: count one deposit as backing for two simultaneous claims

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls the future mask produced by the new debt bit reach `find-superset` (mainnet/contracts/registry/v0-egroup.clar:262) in a state where it count one deposit as backing for two simultaneous claims? Given that it returns the FIRST mask that is a superset, walking buckets in population order rather than finding the tightest, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:262` -> `find-superset`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the future mask produced by the new debt bit
- Exploit idea: `find-superset` returns the FIRST mask that is a superset, walking buckets in population order rather than finding the tightest. Reach it through `borrow` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `borrow` with the future mask produced by the new debt bit, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
