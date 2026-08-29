# Q3580: insert via transfer: make the per-user ledger and the vault aggregate disagree 

## Question
Does `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) let an unprivileged attacker who controls the destination principal, including the market, the market-vault or the treasury reach `insert` (mainnet/contracts/market/v0-market-vault.clar:159) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it rewrites the whole registry entry for a user id, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is theft of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:159` -> `insert`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the destination principal, including the market, the market-vault or the treasury
- Exploit idea: `insert` rewrites the whole registry entry for a user id. Reach it through `transfer` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: Set up the position in simnet, call `transfer` with the destination principal, including the market, the market-vault or the treasury, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
