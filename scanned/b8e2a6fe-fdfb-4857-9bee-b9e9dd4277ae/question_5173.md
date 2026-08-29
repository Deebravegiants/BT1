# Q5173: interest-rate via call-ststx-ratio: leave a residue that no reconciliation pass ever inspects

## Question
Can an unprivileged attacker entering through `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015), controlling whether the ratio is fetched before or after other state changes in the block, drive `interest-rate` (mainnet/contracts/vault/v0-vault-stx.clar:371) — which interpolates the packed curve at the current utilization — to leave a residue that no reconciliation pass ever inspects, breaking the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:371` -> `interest-rate`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: whether the ratio is fetched before or after other state changes in the block
- Exploit idea: `interest-rate` interpolates the packed curve at the current utilization. Reach it through `call-ststx-ratio` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `call-ststx-ratio` with whether the ratio is fetched before or after other state changes in the block, then read `interest-rate` state before and after in the same block and assert the two sides of the invariant are equal.
