# Q2364: write-feed via borrow: credit one side of an accounting pair without the other

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls `receiver`, including a contract principal reach `write-feed` (mainnet/contracts/market/v0-4-market.clar:129) in a state where it credit one side of an accounting pair without the other? Given that it applies one Pyth price-feed update and folds its status, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:129` -> `write-feed`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `write-feed` applies one Pyth price-feed update and folds its status. Reach it through `borrow` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `receiver`, including a contract principal across its boundary values through `borrow` in simnet and assert `write-feed` never returns a value that breaks the invariant.
