# Q2520: subset via collateral-add: credit one side of an accounting pair without the other

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls `amount` reach `subset` (mainnet/contracts/market/v0-market-vault.clar:100) in a state where it credit one side of an accounting pair without the other? Given that it tests bitmask containment, the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:100` -> `subset`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `subset` tests bitmask containment. Reach it through `collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz `amount` across its boundary values through `collateral-add` in simnet and assert `subset` never returns a value that breaks the invariant.
