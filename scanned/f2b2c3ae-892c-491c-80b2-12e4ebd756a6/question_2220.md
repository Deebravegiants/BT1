# Q2220: mask-to-list-collateral via collateral-remove: credit one side of an accounting pair without the other

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls `receiver`, including a contract principal reach `mask-to-list-collateral` (mainnet/contracts/market/v0-4-market.clar:449) in a state where it credit one side of an accounting pair without the other? Given that it expands a mask to a list of ids over ITER-UINT-64, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:449` -> `mask-to-list-collateral`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `mask-to-list-collateral` expands a mask to a list of ids over ITER-UINT-64. Reach it through `collateral-remove` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `receiver`, including a contract principal across its boundary values through `collateral-remove` in simnet and assert `mask-to-list-collateral` never returns a value that breaks the invariant.
