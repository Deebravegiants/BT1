# Q2017: find via borrow: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), controlling the `ft` trait principal, drive `find` (mainnet/contracts/registry/v0-assets.clar:135) — which resolves an asset record from a principal through the `reverse` map — to mint shares whose backing was never received, breaking the invariant that shares outstanding valued at the current share price never exceed `total-assets`, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:135` -> `find`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `find` resolves an asset record from a principal through the `reverse` map. Reach it through `borrow` and mint shares whose backing was never received.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `borrow` with the `ft` trait principal, then read `find` state before and after in the same block and assert the two sides of the invariant are equal.
