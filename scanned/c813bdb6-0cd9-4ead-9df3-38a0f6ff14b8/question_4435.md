# Q4435: iter-find-superset via borrow: credit one side of an accounting pair without the other

## Question
`iter-find-superset` (mainnet/contracts/registry/v0-egroup.clar:267) short-circuits on the first superset match. Can an unprivileged caller of `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), by choosing the future mask produced by the new debt bit, use that to credit one side of an accounting pair without the other, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:267` -> `iter-find-superset`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the future mask produced by the new debt bit
- Exploit idea: `iter-find-superset` short-circuits on the first superset match. Reach it through `borrow` and credit one side of an accounting pair without the other.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `borrow` with the future mask produced by the new debt bit, then read `iter-find-superset` state before and after in the same block and assert the two sides of the invariant are equal.
