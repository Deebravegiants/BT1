# Q0859: accrue via liquidate: have the same quantity scaled twice by two contracts that 

## Question
`accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) advances `last-update` only inside `(if (or (not (is-eq idx next)) ...))`, so an interval whose multiplier rounds to INDEX-PRECISION leaves the clock stale. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing `borrower`, any third-party principal, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:835` -> `accrue`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `borrower`, any third-party principal
- Exploit idea: `accrue` advances `last-update` only inside `(if (or (not (is-eq idx next)) ...))`, so an interval whose multiplier rounds to INDEX-PRECISION leaves the clock stale. Reach it through `liquidate` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate` with `borrower`, any third-party principal, then read `accrue` state before and after in the same block and assert the two sides of the invariant are equal.
