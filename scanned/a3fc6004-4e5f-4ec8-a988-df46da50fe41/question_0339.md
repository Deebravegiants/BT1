# Q0339: get-egroup via supply-collateral-add: have the same quantity scaled twice by two contracts that 

## Question
`get-egroup` (mainnet/contracts/market/v0-4-market.clar:460) resolves the efficiency group for a mask and is unwrapped with `try!` on every health path. Can an unprivileged caller of `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), by choosing vault share price at the moment of the deposit leg, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:460` -> `get-egroup`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: vault share price at the moment of the deposit leg
- Exploit idea: `get-egroup` resolves the efficiency group for a mask and is unwrapped with `try!` on every health path. Reach it through `supply-collateral-add` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `get-egroup` touches, run `supply-collateral-add` with vault share price at the moment of the deposit leg, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
