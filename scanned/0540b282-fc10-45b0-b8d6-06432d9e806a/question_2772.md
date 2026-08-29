# Q2772: find via collateral-add: credit one side of an accounting pair without the other

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls `amount` reach `find` (mainnet/contracts/registry/v0-assets.clar:135) in a state where it credit one side of an accounting pair without the other? Given that it resolves an asset record from a principal through the `reverse` map, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:135` -> `find`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `find` resolves an asset record from a principal through the `reverse` map. Reach it through `collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `amount` across its boundary values through `collateral-add` in simnet and assert `find` never returns a value that breaks the invariant.
