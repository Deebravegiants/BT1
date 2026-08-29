# Q5076: oracle-last-update via collateral-remove: record a repayment larger than the value actually delivere

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls the `price-feeds` buffers reach `oracle-last-update` (mainnet/contracts/market/v0-4-market.clar:939) in a state where it record a repayment larger than the value actually delivered? Given that it returns the stored monotonic timestamp for a `{type, ident}` key shared by every asset using that feed, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:939` -> `oracle-last-update`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `oracle-last-update` returns the stored monotonic timestamp for a `{type, ident}` key shared by every asset using that feed. Reach it through `collateral-remove` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the `price-feeds` buffers across its boundary values through `collateral-remove` in simnet and assert `oracle-last-update` never returns a value that breaks the invariant.
