# Q4014: lookup via collateral-add: destroy value through a truncation the opposite operation 

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling the position's existing collateral and debt composition, can an unprivileged attacker make `lookup` (mainnet/contracts/registry/v0-assets.clar:139) destroy value through a truncation the opposite operation does not restore? `lookup` returns the registry record, including the `decimals` captured once at registration, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:139` -> `lookup`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the position's existing collateral and debt composition
- Exploit idea: `lookup` returns the registry record, including the `decimals` captured once at registration. Reach it through `collateral-add` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz the position's existing collateral and debt composition across its boundary values through `collateral-add` in simnet and assert `lookup` never returns a value that breaks the invariant.
