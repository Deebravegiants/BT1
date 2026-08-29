# Q4459: get-position via collateral-remove-redeem: credit one side of an accounting pair without the other

## Question
`get-position` (mainnet/contracts/market/v0-4-market.clar:466) returns only rows whose bit is set in the ENABLED bitmap. Can an unprivileged caller of `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), by choosing `receiver` for the underlying leg, use that to credit one side of an accounting pair without the other, violating the invariant that shares outstanding valued at the current share price never exceed `total-assets` and producing direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:466` -> `get-position`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `receiver` for the underlying leg
- Exploit idea: `get-position` returns only rows whose bit is set in the ENABLED bitmap. Reach it through `collateral-remove-redeem` and credit one side of an accounting pair without the other.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-remove-redeem` with `receiver` for the underlying leg, then read `get-position` state before and after in the same block and assert the two sides of the invariant are equal.
