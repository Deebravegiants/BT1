# Q1353: total-assets via redeem: make the per-user ledger and the vault aggregate disagree 

## Question
Can an unprivileged attacker entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797), controlling the vault's available liquidity relative to the redemption, drive `total-assets` (mainnet/contracts/vault/v0-vault-stx.clar:334) — which adds `(- debt borrowed)` as accrued interest that no token in the vault yet backs — to make the per-user ledger and the vault aggregate disagree by a repeatable amount, breaking the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:334` -> `total-assets`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: the vault's available liquidity relative to the redemption
- Exploit idea: `total-assets` adds `(- debt borrowed)` as accrued interest that no token in the vault yet backs. Reach it through `redeem` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `total-assets` touches, run `redeem` with the vault's available liquidity relative to the redemption, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
