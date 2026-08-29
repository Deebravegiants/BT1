# Q1403: resolve-interpolation-points via collateral-remove: leave a residue that no reconciliation pass ever inspects

## Question
`resolve-interpolation-points` (mainnet/contracts/vault/v0-vault-stx.clar:205) selects the bracketing curve points for a utilization. Can an unprivileged caller of `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107), by choosing the set of assets held, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:205` -> `resolve-interpolation-points`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the set of assets held
- Exploit idea: `resolve-interpolation-points` selects the bracketing curve points for a utilization. Reach it through `collateral-remove` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `collateral-remove` call, then the attacker-shaped one with the set of assets held, and assert the attacker's net token balance change is zero or negative.
