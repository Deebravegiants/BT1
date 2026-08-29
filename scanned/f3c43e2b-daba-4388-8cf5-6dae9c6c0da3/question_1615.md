# Q1615: convert-to-assets-preview via liquidate-redeem: leave a residue that no reconciliation pass ever inspects

## Question
`convert-to-assets-preview` (mainnet/contracts/vault/v0-vault-stx.clar:317) prices a redemption against `total-assets-preview` and `total-supply-preview`. Can an unprivileged caller of `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), by choosing the borrower targeted, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:317` -> `convert-to-assets-preview`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the borrower targeted
- Exploit idea: `convert-to-assets-preview` prices a redemption against `total-assets-preview` and `total-supply-preview`. Reach it through `liquidate-redeem` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate-redeem` with the borrower targeted, then read `convert-to-assets-preview` state before and after in the same block and assert the two sides of the invariant are equal.
