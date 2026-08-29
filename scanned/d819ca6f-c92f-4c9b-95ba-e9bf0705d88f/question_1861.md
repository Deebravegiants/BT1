# Q1861: vault-system-borrow via liquidate-multi: make the per-user ledger and the vault aggregate disagree 

## Question
Can an unprivileged attacker entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), controlling how many entries share one price snapshot (price-feeds is passed as none), drive `vault-system-borrow` (mainnet/contracts/market/v0-4-market.clar:198) — which routes a borrow to one of six vaults by asset id — to make the per-user ledger and the vault aggregate disagree by a repeatable amount, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:198` -> `vault-system-borrow`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: how many entries share one price snapshot (price-feeds is passed as none)
- Exploit idea: `vault-system-borrow` routes a borrow to one of six vaults by asset id. Reach it through `liquidate-multi` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate-multi` with how many entries share one price snapshot (price-feeds is passed as none), then read `vault-system-borrow` state before and after in the same block and assert the two sides of the invariant are equal.
