# Q4495: debt-preview via collateral-remove-redeem: credit one side of an accounting pair without the other

## Question
`debt-preview` (mainnet/contracts/vault/v0-vault-stx.clar:331) computes cumulative debt from `principal-scaled` and the FORWARD index. Can an unprivileged caller of `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), by choosing the zToken/underlying id mapping reached (the u100 sentinel branch), use that to credit one side of an accounting pair without the other, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:331` -> `debt-preview`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: the zToken/underlying id mapping reached (the u100 sentinel branch)
- Exploit idea: `debt-preview` computes cumulative debt from `principal-scaled` and the FORWARD index. Reach it through `collateral-remove-redeem` and credit one side of an accounting pair without the other.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-remove-redeem` with the zToken/underlying id mapping reached (the u100 sentinel branch), then read `debt-preview` state before and after in the same block and assert the two sides of the invariant are equal.
