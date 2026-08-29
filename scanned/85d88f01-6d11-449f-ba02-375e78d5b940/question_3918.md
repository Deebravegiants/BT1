# Q3918: interest-rate via collateral-add: destroy value through a truncation the opposite operation 

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling the position's existing collateral and debt composition, can an unprivileged attacker make `interest-rate` (mainnet/contracts/vault/v0-vault-stx.clar:371) destroy value through a truncation the opposite operation does not restore? `interest-rate` interpolates the packed curve at the current utilization, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:371` -> `interest-rate`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the position's existing collateral and debt composition
- Exploit idea: `interest-rate` interpolates the packed curve at the current utilization. Reach it through `collateral-add` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the position's existing collateral and debt composition across its boundary values through `collateral-add` in simnet and assert `interest-rate` never returns a value that breaks the invariant.
