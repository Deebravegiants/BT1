# Q0519: iter-find-superset via borrow: have the same quantity scaled twice by two contracts that 

## Question
`iter-find-superset` (mainnet/contracts/registry/v0-egroup.clar:267) short-circuits on the first superset match. Can an unprivileged caller of `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), by choosing the `ft` trait principal, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:267` -> `iter-find-superset`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `iter-find-superset` short-circuits on the first superset match. Reach it through `borrow` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `iter-find-superset` touches, run `borrow` with the `ft` trait principal, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
