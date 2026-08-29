# Q4594: unpack-u16 via redeem: destroy value through a truncation the opposite operation 

## Question
Entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) while controlling `recipient`, can an unprivileged attacker make `unpack-u16` (mainnet/contracts/vault/v0-vault-stx.clar:259) destroy value through a truncation the opposite operation does not restore? `unpack-u16` unpacks eight u16 curve fields from one packed word, so the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:259` -> `unpack-u16`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `recipient`
- Exploit idea: `unpack-u16` unpacks eight u16 curve fields from one packed word. Reach it through `redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `redeem` with `recipient`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
