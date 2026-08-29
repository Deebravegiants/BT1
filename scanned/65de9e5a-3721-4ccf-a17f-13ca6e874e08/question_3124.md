# Q3124: unpack-u16 via collateral-remove: make the per-user ledger and the vault aggregate disagree 

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls `amount` relative to the current collateral row (the removing-all branch) reach `unpack-u16` (mainnet/contracts/vault/v0-vault-stx.clar:259) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it unpacks eight u16 curve fields from one packed word, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is direct theft of user funds at rest or in motion.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:259` -> `unpack-u16`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `amount` relative to the current collateral row (the removing-all branch)
- Exploit idea: `unpack-u16` unpacks eight u16 curve fields from one packed word. Reach it through `collateral-remove` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: Set up the position in simnet, call `collateral-remove` with `amount` relative to the current collateral row (the removing-all branch), and assert on the printed event plus the post-state that collateral, debt and share totals still reconcile.
