# Q5881: active via borrow: destroy value through a truncation the opposite operation 

## Question
Can an unprivileged attacker entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), controlling `amount`, drive `active` (mainnet/contracts/registry/v0-egroup.clar:238) — which lists candidate bucket masks at or above a population — to destroy value through a truncation the opposite operation does not restore, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:238` -> `active`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `active` lists candidate bucket masks at or above a population. Reach it through `borrow` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `borrow` with `amount`, then read `active` state before and after in the same block and assert the two sides of the invariant are equal.
