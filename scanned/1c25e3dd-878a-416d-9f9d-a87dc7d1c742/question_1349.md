# Q1349: calc-treasury-lp-preview via transfer: make the per-user ledger and the vault aggregate disagree 

## Question
Can an unprivileged attacker entering through `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752), controlling the timing relative to a pledge or a liquidation, drive `calc-treasury-lp-preview` (mainnet/contracts/vault/v0-vault-stx.clar:350) — which divides by `(- ta-preview reserve-inc)`, a denominator that can reach zero or underflow — to make the per-user ledger and the vault aggregate disagree by a repeatable amount, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause permanent freezing of unclaimed yield?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:350` -> `calc-treasury-lp-preview`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the timing relative to a pledge or a liquidation
- Exploit idea: `calc-treasury-lp-preview` divides by `(- ta-preview reserve-inc)`, a denominator that can reach zero or underflow. Reach it through `transfer` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Run the baseline `transfer` call, then the attacker-shaped one with the timing relative to a pledge or a liquidation, and assert the attacker's net token balance change is zero or negative.
