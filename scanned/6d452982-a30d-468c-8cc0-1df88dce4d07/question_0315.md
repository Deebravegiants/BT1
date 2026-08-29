# Q0315: population via borrow: have the same quantity scaled twice by two contracts that 

## Question
`population` (mainnet/contracts/registry/v0-egroup.clar:81) counts set bits to order the bucket search. Can an unprivileged caller of `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), by choosing the `ft` trait principal, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:81` -> `population`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `population` counts set bits to order the bucket search. Reach it through `borrow` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `population` touches, run `borrow` with the `ft` trait principal, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
