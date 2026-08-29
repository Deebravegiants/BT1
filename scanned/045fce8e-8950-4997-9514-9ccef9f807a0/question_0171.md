# Q0171: write-feed via supply-collateral-add: have the same quantity scaled twice by two contracts that 

## Question
`write-feed` (mainnet/contracts/market/v0-4-market.clar:129) applies one Pyth price-feed update and folds its status. Can an unprivileged caller of `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), by choosing `amount`, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:129` -> `write-feed`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `write-feed` applies one Pyth price-feed update and folds its status. Reach it through `supply-collateral-add` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `write-feed` touches, run `supply-collateral-add` with `amount`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
