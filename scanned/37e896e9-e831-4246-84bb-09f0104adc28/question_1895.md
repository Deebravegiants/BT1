# Q1895: remove-user-collateral via collateral-remove-redeem: leave a residue that no reconciliation pass ever inspects

## Question
`remove-user-collateral` (mainnet/contracts/market/v0-market-vault.clar:205) asserts sufficiency then `map-delete`s only on an exact zero. Can an unprivileged caller of `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), by choosing `amount` used for BOTH the collateral removal and the share redemption, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:205` -> `remove-user-collateral`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `amount` used for BOTH the collateral removal and the share redemption
- Exploit idea: `remove-user-collateral` asserts sufficiency then `map-delete`s only on an exact zero. Reach it through `collateral-remove-redeem` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `collateral-remove-redeem` call, then the attacker-shaped one with `amount` used for BOTH the collateral removal and the share redemption, and assert the attacker's net token balance change is zero or negative.
