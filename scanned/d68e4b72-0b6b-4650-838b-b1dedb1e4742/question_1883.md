# Q1883: normalize via collateral-remove: leave a residue that no reconciliation pass ever inspects

## Question
`normalize` (mainnet/contracts/market/v0-4-market.clar:576) divides by `(pow u10 decimals)` only AFTER multiplying amount by price, making the protocol's USD unit a whole dollar. Can an unprivileged caller of `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107), by choosing the set of assets held, use that to leave a residue that no reconciliation pass ever inspects, violating the invariant that `principal-scaled` and `total-borrowed` describe the same outstanding principal and producing protocol insolvency?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:576` -> `normalize`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the set of assets held
- Exploit idea: `normalize` divides by `(pow u10 decimals)` only AFTER multiplying amount by price, making the protocol's USD unit a whole dollar. Reach it through `collateral-remove` and leave a residue that no reconciliation pass ever inspects.
- Invariant to test: `principal-scaled` and `total-borrowed` describe the same outstanding principal
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `collateral-remove` call, then the attacker-shaped one with the set of assets held, and assert the attacker's net token balance change is zero or negative.
