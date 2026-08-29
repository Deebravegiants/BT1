# Q5400: find-debt-scaled via collateral-remove: record a repayment larger than the value actually delivere

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls the `price-feeds` buffers reach `find-debt-scaled` (mainnet/contracts/market/v0-4-market.clar:621) in a state where it record a repayment larger than the value actually delivered? Given that it returns u0 for an absent asset, making a missing debt row indistinguishable from no debt, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:621` -> `find-debt-scaled`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `find-debt-scaled` returns u0 for an absent asset, making a missing debt row indistinguishable from no debt. Reach it through `collateral-remove` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the `price-feeds` buffers across its boundary values through `collateral-remove` in simnet and assert `find-debt-scaled` never returns a value that breaks the invariant.
