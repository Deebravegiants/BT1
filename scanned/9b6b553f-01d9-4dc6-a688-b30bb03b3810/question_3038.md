# Q3038: resolve-price-feed via collateral-remove: leave a residue that no reconciliation pass ever inspects

## Question
Entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) while controlling the `price-feeds` buffers, can an unprivileged attacker make `resolve-price-feed` (mainnet/contracts/market/v0-4-market.clar:332) leave a residue that no reconciliation pass ever inspects? `resolve-price-feed` dispatches on a 1-byte type to `resolve-pyth` or `resolve-dia`, erroring otherwise, so the invariant that shares outstanding valued at the current share price never exceed `total-assets` would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:332` -> `resolve-price-feed`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the `price-feeds` buffers
- Exploit idea: `resolve-price-feed` dispatches on a 1-byte type to `resolve-pyth` or `resolve-dia`, erroring otherwise. Reach it through `collateral-remove` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `collateral-remove` twice with the `price-feeds` buffers varied, and assert that the value `resolve-price-feed` returns is identical in both runs; a divergence confirms the finding.
