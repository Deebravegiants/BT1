# Q3211: mask-shift-combine via liquidate: count one deposit as backing for two simultaneous claims

## Question
`mask-shift-combine` (mainnet/contracts/market/v0-4-market.clar:422) folds the 128-bit mask down by shifting the debt half by DEBT-OFFSET and OR-ing it onto the collateral half. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing `collateral-receiver`, use that to count one deposit as backing for two simultaneous claims, violating the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:422` -> `mask-shift-combine`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `collateral-receiver`
- Exploit idea: `mask-shift-combine` folds the 128-bit mask down by shifting the debt half by DEBT-OFFSET and OR-ing it onto the collateral half. Reach it through `liquidate` and count one deposit as backing for two simultaneous claims.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate` with `collateral-receiver`, then read `mask-shift-combine` state before and after in the same block and assert the two sides of the invariant are equal.
