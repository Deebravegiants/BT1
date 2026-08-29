# Q5589: convert-to-assets-preview via transfer: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752), controlling `amount`, drive `convert-to-assets-preview` (mainnet/contracts/vault/v0-vault-stx.clar:317) — which prices a redemption against `total-assets-preview` and `total-supply-preview` — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset, and cause temporary freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:317` -> `convert-to-assets-preview`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `convert-to-assets-preview` prices a redemption against `total-assets-preview` and `total-supply-preview`. Reach it through `transfer` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Snapshot every state variable `convert-to-assets-preview` touches, run `transfer` with `amount`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
