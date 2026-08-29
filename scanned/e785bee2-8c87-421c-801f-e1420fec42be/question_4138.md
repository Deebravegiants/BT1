# Q4138: create via transfer: destroy value through a truncation the opposite operation 

## Question
Entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) while controlling `amount`, can an unprivileged attacker make `create` (mainnet/contracts/market/v0-market-vault.clar:150) destroy value through a truncation the opposite operation does not restore? `create` binds a principal to a fresh numeric id, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:150` -> `create`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `create` binds a principal to a fresh numeric id. Reach it through `transfer` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `transfer` with `amount`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
