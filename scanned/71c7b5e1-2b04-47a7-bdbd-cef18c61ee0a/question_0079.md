# Q0079: population via collateral-add: have the same quantity scaled twice by two contracts that 

## Question
`population` (mainnet/contracts/registry/v0-egroup.clar:81) counts set bits to order the bucket search. Can an unprivileged caller of `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), by choosing the `ft` trait principal, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing theft of unclaimed yield?

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:81` -> `population`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `population` counts set bits to order the bucket search. Reach it through `collateral-add` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-add` with the `ft` trait principal, then read `population` state before and after in the same block and assert the two sides of the invariant are equal.
