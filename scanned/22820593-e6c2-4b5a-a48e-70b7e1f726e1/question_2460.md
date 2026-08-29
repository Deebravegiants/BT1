# Q2460: resolve via collateral-add: credit one side of an accounting pair without the other

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls `amount` reach `resolve` (mainnet/contracts/registry/v0-egroup.clar:360) in a state where it credit one side of an accounting pair without the other? Given that it selects the efficiency group for a position mask, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:360` -> `resolve`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `resolve` selects the efficiency group for a position mask. Reach it through `collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `amount` across its boundary values through `collateral-add` in simnet and assert `resolve` never returns a value that breaks the invariant.
