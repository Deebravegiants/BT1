# Q4318: next-index via deposit: destroy value through a truncation the opposite operation 

## Question
Entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) while controlling `min-out`, can an unprivileged attacker make `next-index` (mainnet/contracts/vault/v0-vault-stx.clar:379) destroy value through a truncation the opposite operation does not restore? `next-index` returns the stale `index` unchanged when the accrue pause state is set, instead of reverting, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:379` -> `next-index`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `min-out`
- Exploit idea: `next-index` returns the stale `index` unchanged when the accrue pause state is set, instead of reverting. Reach it through `deposit` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `deposit` with `min-out`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
