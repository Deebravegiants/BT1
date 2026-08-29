# Q4759: mask-shift-combine via supply-collateral-add: credit one side of an accounting pair without the other

## Question
`mask-shift-combine` (mainnet/contracts/market/v0-4-market.clar:422) folds the 128-bit mask down by shifting the debt half by DEBT-OFFSET and OR-ing it onto the collateral half. Can an unprivileged caller of `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), by choosing the `ft` trait principal deciding which vault is routed to, use that to credit one side of an accounting pair without the other, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing theft of unclaimed yield?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:422` -> `mask-shift-combine`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal deciding which vault is routed to
- Exploit idea: `mask-shift-combine` folds the 128-bit mask down by shifting the debt half by DEBT-OFFSET and OR-ing it onto the collateral half. Reach it through `supply-collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: In `local-testing/tests` on a local fork, drive `supply-collateral-add` with the `ft` trait principal deciding which vault is routed to, then read `mask-shift-combine` state before and after in the same block and assert the two sides of the invariant are equal.
