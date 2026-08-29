# Q3484: interest-rate via borrow: make the per-user ledger and the vault aggregate disagree 

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls `amount` reach `interest-rate` (mainnet/contracts/vault/v0-vault-stx.clar:371) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it interpolates the packed curve at the current utilization, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:371` -> `interest-rate`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `interest-rate` interpolates the packed curve at the current utilization. Reach it through `borrow` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `borrow` with `amount`, and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
