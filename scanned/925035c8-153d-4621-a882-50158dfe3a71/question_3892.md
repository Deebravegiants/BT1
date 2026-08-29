# Q3892: receive-underlying via transfer: make the per-user ledger and the vault aggregate disagree 

## Question
Does `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) let an unprivileged attacker who controls the destination principal, including the market, the market-vault or the treasury reach `receive-underlying` (mainnet/contracts/vault/v0-vault-stx.clar:291) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it pulls the underlying from a named account, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is direct theft of another user's collateral.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:291` -> `receive-underlying`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the destination principal, including the market, the market-vault or the treasury
- Exploit idea: `receive-underlying` pulls the underlying from a named account. Reach it through `transfer` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: Set up the position in simnet, call `transfer` with the destination principal, including the market, the market-vault or the treasury, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
