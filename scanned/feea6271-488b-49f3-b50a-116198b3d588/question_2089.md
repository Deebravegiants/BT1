# Q2089: relevant via repay: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316), controlling the `ft` trait principal, drive `relevant` (mainnet/contracts/market/v0-market-vault.clar:175) — which drops any position row whose bit is not present in the enabled mask — to mint shares whose backing was never received, breaking the invariant that shares outstanding valued at the current share price never exceed `total-assets`, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:175` -> `relevant`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `relevant` drops any position row whose bit is not present in the enabled mask. Reach it through `repay` and mint shares whose backing was never received.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `repay` with the `ft` trait principal, then read `relevant` state before and after in the same block and assert the two sides of the invariant are equal.
