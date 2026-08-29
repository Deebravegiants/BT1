# Q2808: vault-accrue via collateral-remove: credit one side of an accounting pair without the other

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls `receiver`, including a contract principal reach `vault-accrue` (mainnet/contracts/market/v0-4-market.clar:189) in a state where it credit one side of an accounting pair without the other? Given that it dispatches accrual to one of six vaults by asset id, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:189` -> `vault-accrue`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `receiver`, including a contract principal
- Exploit idea: `vault-accrue` dispatches accrual to one of six vaults by asset id. Reach it through `collateral-remove` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz `receiver`, including a contract principal across its boundary values through `collateral-remove` in simnet and assert `vault-accrue` never returns a value that breaks the invariant.
