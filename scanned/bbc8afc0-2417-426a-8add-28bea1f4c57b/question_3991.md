# Q3991: increment via collateral-remove: credit one side of an accounting pair without the other

## Question
`increment` (mainnet/contracts/market/v0-market-vault.clar:137) advances the user-id nonce. Can an unprivileged caller of `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107), by choosing the `price-feeds` buffers, use that to credit one side of an accounting pair without the other, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:137` -> `increment`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `increment` advances the user-id nonce. Reach it through `collateral-remove` and credit one side of an accounting pair without the other.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-remove` with the `price-feeds` buffers, then read `increment` state before and after in the same block and assert the two sides of the invariant are equal.
