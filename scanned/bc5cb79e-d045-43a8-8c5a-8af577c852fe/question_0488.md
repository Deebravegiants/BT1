# Q0488: debt-preview via transfer: destroy value through a truncation the opposite operation 

## Question
Does `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752) let an unprivileged attacker who controls `amount` reach `debt-preview` (mainnet/contracts/vault/v0-vault-stx.clar:331) in a state where it destroy value through a truncation the opposite operation does not restore? Given that it computes cumulative debt from `principal-scaled` and the FORWARD index, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:331` -> `debt-preview`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `debt-preview` computes cumulative debt from `principal-scaled` and the FORWARD index. Reach it through `transfer` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `transfer` twice with `amount` varied, and assert that the value `debt-preview` returns is identical in both runs; a divergence confirms the finding.
