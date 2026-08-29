# Q4207: get-position via liquidate-redeem: credit one side of an accounting pair without the other

## Question
`get-position` (mainnet/contracts/market/v0-4-market.clar:466) returns only rows whose bit is set in the ENABLED bitmap. Can an unprivileged caller of `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), by choosing the vault whose share price the redemption moves, use that to credit one side of an accounting pair without the other, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:466` -> `get-position`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the vault whose share price the redemption moves
- Exploit idea: `get-position` returns only rows whose bit is set in the ENABLED bitmap. Reach it through `liquidate-redeem` and credit one side of an accounting pair without the other.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate-redeem` with the vault whose share price the redemption moves, then read `get-position` state before and after in the same block and assert the two sides of the invariant are equal.
