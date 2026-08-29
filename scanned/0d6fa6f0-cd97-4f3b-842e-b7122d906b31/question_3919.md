# Q3919: price-resolve via call-ststx-ratio: credit one side of an accounting pair without the other

## Question
`price-resolve` (mainnet/contracts/market/v0-4-market.clar:373) resolves a feed, applies the callcode transform, then checks `oracle-price-legal` and `oracle-timestamp-fresh` on the POST-transform value while advancing the per-key `last-update` only when the new timestamp is greater. Can an unprivileged caller of `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015), by choosing the block and transaction position at which the external ratio is fetched, use that to credit one side of an accounting pair without the other, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:373` -> `price-resolve`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: the block and transaction position at which the external ratio is fetched
- Exploit idea: `price-resolve` resolves a feed, applies the callcode transform, then checks `oracle-price-legal` and `oracle-timestamp-fresh` on the POST-transform value while advancing the per-key `last-update` only when the new timestamp is greater. Reach it through `call-ststx-ratio` and credit one side of an accounting pair without the other.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `call-ststx-ratio` with the block and transaction position at which the external ratio is fetched, then read `price-resolve` state before and after in the same block and assert the two sides of the invariant are equal.
