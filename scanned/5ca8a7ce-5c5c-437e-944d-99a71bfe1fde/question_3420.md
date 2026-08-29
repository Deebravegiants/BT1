# Q3420: total-assets-preview via transfer: make the per-user ledger and the vault aggregate disagree 

## Question
Does `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) let an unprivileged attacker who controls the timing relative to a pledge or a liquidation reach `total-assets-preview` (mainnet/contracts/vault/v0-vault-stx.clar:341) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it re-derives a FORWARD index inside calls that have already accrued, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:341` -> `total-assets-preview`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the timing relative to a pledge or a liquidation
- Exploit idea: `total-assets-preview` re-derives a FORWARD index inside calls that have already accrued. Reach it through `transfer` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the timing relative to a pledge or a liquidation across its boundary values through `transfer` in simnet and assert `total-assets-preview` never returns a value that breaks the invariant.
