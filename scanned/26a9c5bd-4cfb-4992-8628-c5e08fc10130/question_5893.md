# Q5893: mask-update via repay: destroy value through a truncation the opposite operation 

## Question
Can an unprivileged attacker entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316), controlling the `ft` trait principal, drive `mask-update` (mainnet/contracts/market/v0-market-vault.clar:94) — which sets or clears one bit, clearing only when the row reaches exactly zero — to destroy value through a truncation the opposite operation does not restore, breaking the invariant that shares outstanding valued at the current share price never exceed `total-assets`, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:94` -> `mask-update`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `mask-update` sets or clears one bit, clearing only when the row reaches exactly zero. Reach it through `repay` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `repay` with the `ft` trait principal, then read `mask-update` state before and after in the same block and assert the two sides of the invariant are equal.
