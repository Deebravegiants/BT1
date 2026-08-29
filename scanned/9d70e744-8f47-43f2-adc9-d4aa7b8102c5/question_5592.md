# Q5592: mask-update via collateral-remove: record a repayment larger than the value actually delivere

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls the `price-feeds` buffers reach `mask-update` (mainnet/contracts/market/v0-market-vault.clar:94) in a state where it record a repayment larger than the value actually delivered? Given that it sets or clears one bit, clearing only when the row reaches exactly zero, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:94` -> `mask-update`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `mask-update` sets or clears one bit, clearing only when the row reaches exactly zero. Reach it through `collateral-remove` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the `price-feeds` buffers across its boundary values through `collateral-remove` in simnet and assert `mask-update` never returns a value that breaks the invariant.
