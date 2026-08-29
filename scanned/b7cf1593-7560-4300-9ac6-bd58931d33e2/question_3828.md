# Q3828: total-supply-preview via transfer: make the per-user ledger and the vault aggregate disagree 

## Question
Does `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) let an unprivileged attacker who controls the timing relative to a pledge or a liquidation reach `total-supply-preview` (mainnet/contracts/vault/v0-vault-stx.clar:363) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it adds the not-yet-minted `calc-treasury-lp-preview` to the live supply that both conversions price against, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:363` -> `total-supply-preview`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the timing relative to a pledge or a liquidation
- Exploit idea: `total-supply-preview` adds the not-yet-minted `calc-treasury-lp-preview` to the live supply that both conversions price against. Reach it through `transfer` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz the timing relative to a pledge or a liquidation across its boundary values through `transfer` in simnet and assert `total-supply-preview` never returns a value that breaks the invariant.
