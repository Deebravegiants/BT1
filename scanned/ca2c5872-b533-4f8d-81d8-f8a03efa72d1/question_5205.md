# Q5205: convert-to-assets-preview via accrue: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835), controlling the utilization the rate is interpolated at, drive `convert-to-assets-preview` (mainnet/contracts/vault/v0-vault-stx.clar:317) — which prices a redemption against `total-assets-preview` and `total-supply-preview` — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:317` -> `convert-to-assets-preview`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the utilization the rate is interpolated at
- Exploit idea: `convert-to-assets-preview` prices a redemption against `total-assets-preview` and `total-supply-preview`. Reach it through `accrue` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `convert-to-assets-preview` touches, run `accrue` with the utilization the rate is interpolated at, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
