# Q1045: get-account-scaled-debt via liquidate-multi: make the per-user ledger and the vault aggregate disagree 

## Question
Can an unprivileged attacker entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), controlling how many entries share one price snapshot (price-feeds is passed as none), drive `get-account-scaled-debt` (mainnet/contracts/market/v0-market-vault.clar:307) — which reads one scaled debt row — to make the per-user ledger and the vault aggregate disagree by a repeatable amount, breaking the invariant that every round-up has a paired round-down that repetition cannot exploit, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:307` -> `get-account-scaled-debt`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: how many entries share one price snapshot (price-feeds is passed as none)
- Exploit idea: `get-account-scaled-debt` reads one scaled debt row. Reach it through `liquidate-multi` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate-multi` with how many entries share one price snapshot (price-feeds is passed as none), then read `get-account-scaled-debt` state before and after in the same block and assert the two sides of the invariant are equal.
