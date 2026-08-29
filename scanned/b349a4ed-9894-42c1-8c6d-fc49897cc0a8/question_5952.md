# Q5952: get-liquidation-position via collateral-remove-redeem: have the same quantity scaled twice by two contracts that 

## Question
Does `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) let an unprivileged attacker who controls `receiver` for the underlying leg reach `get-liquidation-position` (mainnet/contracts/market/v0-4-market.clar:473) in a state where it have the same quantity scaled twice by two contracts that round differently? Given that it returns enabled collateral plus ALL debt, a different view from the one borrow validated against, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:473` -> `get-liquidation-position`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `receiver` for the underlying leg
- Exploit idea: `get-liquidation-position` returns enabled collateral plus ALL debt, a different view from the one borrow validated against. Reach it through `collateral-remove-redeem` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `receiver` for the underlying leg across its boundary values through `collateral-remove-redeem` in simnet and assert `get-liquidation-position` never returns a value that breaks the invariant.
