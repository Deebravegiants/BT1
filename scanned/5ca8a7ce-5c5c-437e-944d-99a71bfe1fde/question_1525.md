# Q1525: debt-preview via redeem: make the per-user ledger and the vault aggregate disagree 

## Question
Can an unprivileged attacker entering through `redeem` (mainnet/contracts/vault/v0-vault-stx.clar:797), controlling `amount` of shares burned, drive `debt-preview` (mainnet/contracts/vault/v0-vault-stx.clar:331) — which computes cumulative debt from `principal-scaled` and the FORWARD index — to make the per-user ledger and the vault aggregate disagree by a repeatable amount, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:331` -> `debt-preview`
- Entrypoint: `redeem` (`mainnet/contracts/vault/v0-vault-stx.clar:797`), unprivileged and publicly callable
- Attacker controls: `amount` of shares burned
- Exploit idea: `debt-preview` computes cumulative debt from `principal-scaled` and the FORWARD index. Reach it through `redeem` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `redeem` with `amount` of shares burned, then read `debt-preview` state before and after in the same block and assert the two sides of the invariant are equal.
