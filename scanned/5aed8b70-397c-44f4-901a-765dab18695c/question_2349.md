# Q2349: insert via supply-collateral-add: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), controlling `amount`, drive `insert` (mainnet/contracts/market/v0-market-vault.clar:159) — which rewrites the whole registry entry for a user id — to mint shares whose backing was never received, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause temporary freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:159` -> `insert`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `insert` rewrites the whole registry entry for a user id. Reach it through `supply-collateral-add` and mint shares whose backing was never received.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Snapshot every state variable `insert` touches, run `supply-collateral-add` with `amount`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
