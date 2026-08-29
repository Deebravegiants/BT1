# Q4031: linear-interpolate via collateral-remove-redeem: credit one side of an accounting pair without the other

## Question
`linear-interpolate` (mainnet/contracts/vault/v0-vault-stx.clar:221) interpolates between two points, dividing by `(- x2 x1)`. Can an unprivileged caller of `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), by choosing remaining zToken collateral whose price moves with the redeem, use that to credit one side of an accounting pair without the other, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:221` -> `linear-interpolate`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: remaining zToken collateral whose price moves with the redeem
- Exploit idea: `linear-interpolate` interpolates between two points, dividing by `(- x2 x1)`. Reach it through `collateral-remove-redeem` and credit one side of an accounting pair without the other.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `collateral-remove-redeem` call, then the attacker-shaped one with remaining zToken collateral whose price moves with the redeem, and assert the attacker's net token balance change is zero or negative.
