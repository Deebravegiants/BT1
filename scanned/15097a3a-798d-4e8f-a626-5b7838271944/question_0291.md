# Q0291: get-position via liquidate-redeem: have the same quantity scaled twice by two contracts that 

## Question
`get-position` (mainnet/contracts/market/v0-4-market.clar:466) returns only rows whose bit is set in the ENABLED bitmap. Can an unprivileged caller of `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), by choosing the vault whose share price the redemption moves, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:466` -> `get-position`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the vault whose share price the redemption moves
- Exploit idea: `get-position` returns only rows whose bit is set in the ENABLED bitmap. Reach it through `liquidate-redeem` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `get-position` touches, run `liquidate-redeem` with the vault whose share price the redemption moves, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
