# Q1831: send-tokens via collateral-add: leave a residue that no reconciliation pass ever inspects

## Question
`send-tokens` (mainnet/contracts/market/v0-market-vault.clar:259) pushes an asset to a caller-chosen recipient principal. Can an unprivileged caller of `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), by choosing `amount`, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:259` -> `send-tokens`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `send-tokens` pushes an asset to a caller-chosen recipient principal. Reach it through `collateral-add` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-add` with `amount`, then read `send-tokens` state before and after in the same block and assert the two sides of the invariant are equal.
