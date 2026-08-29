# Q0415: insert via repay: have the same quantity scaled twice by two contracts that 

## Question
`insert` (mainnet/contracts/market/v0-market-vault.clar:159) rewrites the whole registry entry for a user id. Can an unprivileged caller of `repay` (mainnet/contracts/market/v0-4-market.clar:1316), by choosing the `ft` trait principal, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:159` -> `insert`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `insert` rewrites the whole registry entry for a user id. Reach it through `repay` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `repay` with the `ft` trait principal, then read `insert` state before and after in the same block and assert the two sides of the invariant are equal.
