# Q0819: mask-to-list-internal via borrow: have the same quantity scaled twice by two contracts that 

## Question
`mask-to-list-internal` (mainnet/contracts/market/v0-4-market.clar:435) expands mask bits into a list bounded at 64 entries. Can an unprivileged caller of `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), by choosing the `ft` trait principal, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing temporary freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:435` -> `mask-to-list-internal`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `mask-to-list-internal` expands mask bits into a list bounded at 64 entries. Reach it through `borrow` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Snapshot every state variable `mask-to-list-internal` touches, run `borrow` with the `ft` trait principal, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
