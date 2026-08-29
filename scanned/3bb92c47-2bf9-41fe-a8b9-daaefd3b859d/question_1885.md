# Q1885: remove-user-collateral via collateral-add: make the per-user ledger and the vault aggregate disagree 

## Question
Can an unprivileged attacker entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), controlling `amount`, drive `remove-user-collateral` (mainnet/contracts/market/v0-market-vault.clar:205) — which asserts sufficiency then `map-delete`s only on an exact zero — to make the per-user ledger and the vault aggregate disagree by a repeatable amount, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:205` -> `remove-user-collateral`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `remove-user-collateral` asserts sufficiency then `map-delete`s only on an exact zero. Reach it through `collateral-add` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-add` with `amount`, then read `remove-user-collateral` state before and after in the same block and assert the two sides of the invariant are equal.
