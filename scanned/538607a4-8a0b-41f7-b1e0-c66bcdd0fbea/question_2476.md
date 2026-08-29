# Q2476: convert-to-shares-preview via transfer: credit one side of an accounting pair without the other

## Question
Does `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) let an unprivileged attacker who controls the timing relative to a pledge or a liquidation reach `convert-to-shares-preview` (mainnet/contracts/vault/v0-vault-stx.clar:308) in a state where it credit one side of an accounting pair without the other? Given that it returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit, the invariant that `assets` never exceeds the underlying the vault actually holds breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:308` -> `convert-to-shares-preview`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the timing relative to a pledge or a liquidation
- Exploit idea: `convert-to-shares-preview` returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit. Reach it through `transfer` and credit one side of an accounting pair without the other.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `transfer` with the timing relative to a pledge or a liquidation, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
