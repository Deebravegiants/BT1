# Q2535: get-egroup via collateral-remove-redeem: destroy value through a truncation the opposite operation 

## Question
`get-egroup` (mainnet/contracts/market/v0-4-market.clar:460) resolves the efficiency group for a mask and is unwrapped with `try!` on every health path. Can an unprivileged caller of `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), by choosing `min-underlying`, use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that value leaving a call equals value entering plus value minted minus value burned and producing permanent freezing of a position that can never be closed?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:460` -> `get-egroup`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `min-underlying`
- Exploit idea: `get-egroup` resolves the efficiency group for a mask and is unwrapped with `try!` on every health path. Reach it through `collateral-remove-redeem` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Snapshot every state variable `get-egroup` touches, run `collateral-remove-redeem` with `min-underlying`, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
