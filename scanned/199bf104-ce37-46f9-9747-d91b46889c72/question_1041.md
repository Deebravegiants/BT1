# Q1041: insert via collateral-add: make the per-user ledger and the vault aggregate disagree 

## Question
Can an unprivileged attacker entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), controlling the position's existing collateral and debt composition, drive `insert` (mainnet/contracts/market/v0-market-vault.clar:159) — which rewrites the whole registry entry for a user id — to make the per-user ledger and the vault aggregate disagree by a repeatable amount, breaking the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset, and cause permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:159` -> `insert`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the position's existing collateral and debt composition
- Exploit idea: `insert` rewrites the whole registry entry for a user id. Reach it through `collateral-add` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `insert` touches, run `collateral-add` with the position's existing collateral and debt composition, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
