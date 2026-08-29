# Q4231: population via borrow: credit one side of an accounting pair without the other

## Question
`population` (mainnet/contracts/registry/v0-egroup.clar:81) counts set bits to order the bucket search. Can an unprivileged caller of `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), by choosing the future mask produced by the new debt bit, use that to credit one side of an accounting pair without the other, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:81` -> `population`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the future mask produced by the new debt bit
- Exploit idea: `population` counts set bits to order the bucket search. Reach it through `borrow` and credit one side of an accounting pair without the other.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `borrow` with the future mask produced by the new debt bit, then read `population` state before and after in the same block and assert the two sides of the invariant are equal.
