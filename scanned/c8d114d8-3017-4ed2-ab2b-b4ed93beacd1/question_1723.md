# Q1723: resolve-or-create via collateral-remove-redeem: leave a residue that no reconciliation pass ever inspects

## Question
`resolve-or-create` (mainnet/contracts/market/v0-market-vault.clar:143) allocates a user id through `increment` for whatever principal the market names. Can an unprivileged caller of `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), by choosing the zToken/underlying id mapping reached (the u100 sentinel branch), use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal and producing direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:143` -> `resolve-or-create`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: the zToken/underlying id mapping reached (the u100 sentinel branch)
- Exploit idea: `resolve-or-create` allocates a user id through `increment` for whatever principal the market names. Reach it through `collateral-remove-redeem` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-remove-redeem` with the zToken/underlying id mapping reached (the u100 sentinel branch), then read `resolve-or-create` state before and after in the same block and assert the two sides of the invariant are equal.
