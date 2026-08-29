# Q3404: remove-user-collateral via transfer: make the per-user ledger and the vault aggregate disagree 

## Question
Does `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) let an unprivileged attacker who controls `amount` reach `remove-user-collateral` (mainnet/contracts/market/v0-market-vault.clar:205) in a state where it make the per-user ledger and the vault aggregate disagree by a repeatable amount? Given that it asserts sufficiency then `map-delete`s only on an exact zero, the invariant that value leaving a call equals value entering plus value minted minus value burned breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:205` -> `remove-user-collateral`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `remove-user-collateral` asserts sufficiency then `map-delete`s only on an exact zero. Reach it through `transfer` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `transfer` twice with `amount` varied, and assert that the value `remove-user-collateral` returns is identical in both runs; a divergence confirms the finding.
