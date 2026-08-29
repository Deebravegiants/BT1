# Q4687: write-feeds via liquidate: credit one side of an accounting pair without the other

## Question
`write-feeds` (mainnet/contracts/market/v0-4-market.clar:149) folds up to three attacker-supplied buffers through `write-feed` with a `(response bool uint)` accumulator. Can an unprivileged caller of `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), by choosing which collateral and debt asset pair is targeted, use that to credit one side of an accounting pair without the other, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:149` -> `write-feeds`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: which collateral and debt asset pair is targeted
- Exploit idea: `write-feeds` folds up to three attacker-supplied buffers through `write-feed` with a `(response bool uint)` accumulator. Reach it through `liquidate` and credit one side of an accounting pair without the other.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate` with which collateral and debt asset pair is targeted, then read `write-feeds` state before and after in the same block and assert the two sides of the invariant are equal.
