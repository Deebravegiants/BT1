# Q2676: get-cached-indexes via deposit: credit one side of an accounting pair without the other

## Question
Does `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) let an unprivileged attacker who controls `recipient`, including a contract principal reach `get-cached-indexes` (mainnet/contracts/market/v0-4-market.clar:944) in a state where it credit one side of an accounting pair without the other? Given that it reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:944` -> `get-cached-indexes`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `recipient`, including a contract principal
- Exploit idea: `get-cached-indexes` reads the per-block cache entry that `resolve-ztoken` and the debt conversions depend on. Reach it through `deposit` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `recipient`, including a contract principal across its boundary values through `deposit` in simnet and assert `get-cached-indexes` never returns a value that breaks the invariant.
