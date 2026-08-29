# Q2892: get-full-position via collateral-remove: credit one side of an accounting pair without the other

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls `receiver`, including a contract principal reach `get-full-position` (mainnet/contracts/market/v0-4-market.clar:470) in a state where it credit one side of an accounting pair without the other? Given that it returns all collateral rows regardless of the enabled bitmap, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:470` -> `get-full-position`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `get-full-position` returns all collateral rows regardless of the enabled bitmap. Reach it through `collateral-remove` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `receiver`, including a contract principal across its boundary values through `collateral-remove` in simnet and assert `get-full-position` never returns a value that breaks the invariant.
