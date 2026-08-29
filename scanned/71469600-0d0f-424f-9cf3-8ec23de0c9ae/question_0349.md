# Q0349: mask-to-list-internal via liquidate: credit one side of an accounting pair without the other

## Question
Can an unprivileged attacker entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), controlling `borrower`, any third-party principal, drive `mask-to-list-internal` (mainnet/contracts/market/v0-4-market.clar:435) — which expands mask bits into a list bounded at 64 entries — to credit one side of an accounting pair without the other, breaking the invariant that value leaving a call equals value entering plus value minted minus value burned, and cause theft of unclaimed yield?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:435` -> `mask-to-list-internal`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `borrower`, any third-party principal
- Exploit idea: `mask-to-list-internal` expands mask bits into a list bounded at 64 entries. Reach it through `liquidate` and credit one side of an accounting pair without the other.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate` with `borrower`, any third-party principal, then read `mask-to-list-internal` state before and after in the same block and assert the two sides of the invariant are equal.
