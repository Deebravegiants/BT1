# Q4422: accrue-user-collateral via deposit: destroy value through a truncation the opposite operation 

## Question
Entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) while controlling `amount`, can an unprivileged attacker make `accrue-user-collateral` (mainnet/contracts/market/v0-4-market.clar:270) destroy value through a truncation the opposite operation does not restore? `accrue-user-collateral` accrues only rows that `is-ztoken` recognises, skipping everything else, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:270` -> `accrue-user-collateral`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `accrue-user-collateral` accrues only rows that `is-ztoken` recognises, skipping everything else. Reach it through `deposit` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `amount` across its boundary values through `deposit` in simnet and assert `accrue-user-collateral` never returns a value that breaks the invariant.
