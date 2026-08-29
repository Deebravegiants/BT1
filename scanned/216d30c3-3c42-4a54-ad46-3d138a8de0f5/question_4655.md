# Q4655: get-position via collateral-add: credit one side of an accounting pair without the other

## Question
`get-position` (mainnet/contracts/market/v0-4-market.clar:466) returns only rows whose bit is set in the ENABLED bitmap. Can an unprivileged caller of `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), by choosing the three `price-feeds` buffers and their order, use that to credit one side of an accounting pair without the other, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing protocol insolvency?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:466` -> `get-position`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the three `price-feeds` buffers and their order
- Exploit idea: `get-position` returns only rows whose bit is set in the ENABLED bitmap. Reach it through `collateral-add` and credit one side of an accounting pair without the other.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `collateral-add` call, then the attacker-shaped one with the three `price-feeds` buffers and their order, and assert the attacker's net token balance change is zero or negative.
