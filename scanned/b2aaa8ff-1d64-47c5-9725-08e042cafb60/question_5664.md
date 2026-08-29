# Q5664: find via collateral-remove: record a repayment larger than the value actually delivere

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls the `price-feeds` buffers reach `find` (mainnet/contracts/registry/v0-assets.clar:135) in a state where it record a repayment larger than the value actually delivered? Given that it resolves an asset record from a principal through the `reverse` map, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:135` -> `find`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `find` resolves an asset record from a principal through the `reverse` map. Reach it through `collateral-remove` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the `price-feeds` buffers across its boundary values through `collateral-remove` in simnet and assert `find` never returns a value that breaks the invariant.
