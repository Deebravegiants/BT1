# Q5413: convert-to-shares-preview via transfer: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752), controlling the timing relative to a pledge or a liquidation, drive `convert-to-shares-preview` (mainnet/contracts/vault/v0-vault-stx.clar:308) — which returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:308` -> `convert-to-shares-preview`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the timing relative to a pledge or a liquidation
- Exploit idea: `convert-to-shares-preview` returns u0 outright when `total-assets-preview` is non-zero and supply is zero, minting nothing for a real deposit. Reach it through `transfer` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `transfer` with the timing relative to a pledge or a liquidation, then read `convert-to-shares-preview` state before and after in the same block and assert the two sides of the invariant are equal.
