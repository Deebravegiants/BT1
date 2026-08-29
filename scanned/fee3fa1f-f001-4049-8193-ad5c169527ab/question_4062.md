# Q4062: remove-user-collateral via supply-collateral-add: destroy value through a truncation the opposite operation 

## Question
Entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) while controlling `amount`, can an unprivileged attacker make `remove-user-collateral` (mainnet/contracts/market/v0-market-vault.clar:205) destroy value through a truncation the opposite operation does not restore? `remove-user-collateral` asserts sufficiency then `map-delete`s only on an exact zero, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:205` -> `remove-user-collateral`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `remove-user-collateral` asserts sufficiency then `map-delete`s only on an exact zero. Reach it through `supply-collateral-add` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `amount` across its boundary values through `supply-collateral-add` in simnet and assert `remove-user-collateral` never returns a value that breaks the invariant.
