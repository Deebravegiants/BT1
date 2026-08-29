# Q2388: resolve-price-feed via borrow: credit one side of an accounting pair without the other

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls `receiver`, including a contract principal reach `resolve-price-feed` (mainnet/contracts/market/v0-4-market.clar:332) in a state where it credit one side of an accounting pair without the other? Given that it dispatches on a 1-byte type to `resolve-pyth` or `resolve-dia`, erroring otherwise, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:332` -> `resolve-price-feed`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `resolve-price-feed` dispatches on a 1-byte type to `resolve-pyth` or `resolve-dia`, erroring otherwise. Reach it through `borrow` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `receiver`, including a contract principal across its boundary values through `borrow` in simnet and assert `resolve-price-feed` never returns a value that breaks the invariant.
