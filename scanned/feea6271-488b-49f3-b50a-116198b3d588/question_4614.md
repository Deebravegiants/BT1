# Q4614: calc-cumulative-debt via redeem: destroy value through a truncation the opposite operation 

## Question
Entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) while controlling `recipient`, can an unprivileged attacker make `calc-cumulative-debt` (mainnet/contracts/vault/v0-vault-stx.clar:180) destroy value through a truncation the opposite operation does not restore? `calc-cumulative-debt` multiplies scaled principal by an index, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:180` -> `calc-cumulative-debt`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `recipient`
- Exploit idea: `calc-cumulative-debt` multiplies scaled principal by an index. Reach it through `redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `recipient` across its boundary values through `redeem` in simnet and assert `calc-cumulative-debt` never returns a value that breaks the invariant.
