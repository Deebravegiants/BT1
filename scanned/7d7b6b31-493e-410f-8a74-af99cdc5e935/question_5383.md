# Q5383: debt-preview via transfer: make the per-user ledger and the vault aggregate disagree 

## Question
`debt-preview` (mainnet/contracts/vault/v0-vault-stx.clar:331) computes cumulative debt from `principal-scaled` and the FORWARD index. Can an unprivileged caller of `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752), by choosing the timing relative to a pledge or a liquidation, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:331` -> `debt-preview`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the timing relative to a pledge or a liquidation
- Exploit idea: `debt-preview` computes cumulative debt from `principal-scaled` and the FORWARD index. Reach it through `transfer` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `transfer` with the timing relative to a pledge or a liquidation, then read `debt-preview` state before and after in the same block and assert the two sides of the invariant are equal.
