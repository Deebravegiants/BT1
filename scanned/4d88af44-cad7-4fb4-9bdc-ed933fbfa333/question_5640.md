# Q5640: find-superset via collateral-remove: record a repayment larger than the value actually delivere

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls the `price-feeds` buffers reach `find-superset` (mainnet/contracts/registry/v0-egroup.clar:262) in a state where it record a repayment larger than the value actually delivered? Given that it returns the FIRST mask that is a superset, walking buckets in population order rather than finding the tightest, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:262` -> `find-superset`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `find-superset` returns the FIRST mask that is a superset, walking buckets in population order rather than finding the tightest. Reach it through `collateral-remove` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the `price-feeds` buffers across its boundary values through `collateral-remove` in simnet and assert `find-superset` never returns a value that breaks the invariant.
