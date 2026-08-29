# Q2601: insert via transfer: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752), controlling `amount`, drive `insert` (mainnet/contracts/market/v0-market-vault.clar:159) — which rewrites the whole registry entry for a user id — to mint shares whose backing was never received, breaking the invariant that shares outstanding valued at the current share price never exceed `total-assets`, and cause permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:159` -> `insert`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `insert` rewrites the whole registry entry for a user id. Reach it through `transfer` and mint shares whose backing was never received.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `insert` touches, run `transfer` with `amount`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
