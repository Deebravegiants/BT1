# Q1356: calculate-asset-notional-value via collateral-remove: count one deposit as backing for two simultaneous claims

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls `amount` relative to the current collateral row (the removing-all branch) reach `calculate-asset-notional-value` (mainnet/contracts/market/v0-4-market.clar:544) in a state where it count one deposit as backing for two simultaneous claims? Given that it normalizes collateral with round-down and debt with round-up, and calls `accrue-and-cache` with `unwrap-panic` inside the fold, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:544` -> `calculate-asset-notional-value`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `amount` relative to the current collateral row (the removing-all branch)
- Exploit idea: `calculate-asset-notional-value` normalizes collateral with round-down and debt with round-up, and calls `accrue-and-cache` with `unwrap-panic` inside the fold. Reach it through `collateral-remove` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `amount` relative to the current collateral row (the removing-all branch) across its boundary values through `collateral-remove` in simnet and assert `calculate-asset-notional-value` never returns a value that breaks the invariant.
