# Q4583: debt-remove-scaled via collateral-remove-redeem: credit one side of an accounting pair without the other

## Question
`debt-remove-scaled` (mainnet/contracts/market/v0-market-vault.clar:473) clears the debt bit only when the remaining scaled debt is exactly zero. Can an unprivileged caller of `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), by choosing `min-underlying`, use that to credit one side of an accounting pair without the other, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing protocol insolvency?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:473` -> `debt-remove-scaled`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `min-underlying`
- Exploit idea: `debt-remove-scaled` clears the debt bit only when the remaining scaled debt is exactly zero. Reach it through `collateral-remove-redeem` and credit one side of an accounting pair without the other.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `collateral-remove-redeem` call, then the attacker-shaped one with `min-underlying`, and assert the attacker's net token balance change is zero or negative.
