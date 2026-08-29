# Q4462: debt-preview via redeem: destroy value through a truncation the opposite operation 

## Question
Entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797) while controlling `amount` of shares burned, can an unprivileged attacker make `debt-preview` (mainnet/contracts/vault/v0-vault-stx.clar:331) destroy value through a truncation the opposite operation does not restore? `debt-preview` computes cumulative debt from `principal-scaled` and the FORWARD index, so the invariant that `assets` never exceeds the underlying the vault actually holds would fail, yielding direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:331` -> `debt-preview`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `amount` of shares burned
- Exploit idea: `debt-preview` computes cumulative debt from `principal-scaled` and the FORWARD index. Reach it through `redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `redeem` with `amount` of shares burned, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
