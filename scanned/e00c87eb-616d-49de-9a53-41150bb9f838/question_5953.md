# Q5953: population via collateral-add: destroy value through a truncation the opposite operation 

## Question
Can an unprivileged attacker entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), controlling the `ft` trait principal, drive `population` (mainnet/contracts/registry/v0-egroup.clar:81) — which counts set bits to order the bucket search — to destroy value through a truncation the opposite operation does not restore, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:81` -> `population`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `population` counts set bits to order the bucket search. Reach it through `collateral-add` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-add` with the `ft` trait principal, then read `population` state before and after in the same block and assert the two sides of the invariant are equal.
