# Q2628: get-egroup via liquidate: credit one side of an accounting pair without the other

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `debt-amount` reach `get-egroup` (mainnet/contracts/market/v0-4-market.clar:460) in a state where it credit one side of an accounting pair without the other? Given that it resolves the efficiency group for a mask and is unwrapped with `try!` on every health path, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:460` -> `get-egroup`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `debt-amount`
- Exploit idea: `get-egroup` resolves the efficiency group for a mask and is unwrapped with `try!` on every health path. Reach it through `liquidate` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz `debt-amount` across its boundary values through `liquidate` in simnet and assert `get-egroup` never returns a value that breaks the invariant.
