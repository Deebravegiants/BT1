# Q2367: accrue-collateral-asset via repay: destroy value through a truncation the opposite operation 

## Question
`accrue-collateral-asset` (mainnet/contracts/market/v0-4-market.clar:273) maps a ztoken id to a vault id through a chain of `is-eq` tests that falls through to the u100 sentinel. Can an unprivileged caller of `repay` (mainnet/contracts/market/v0-4-market.clar:1316), by choosing `amount`, including far above the real debt (the capping path), use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that value leaving a call equals value entering plus value minted minus value burned and producing permanent freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:273` -> `accrue-collateral-asset`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `amount`, including far above the real debt (the capping path)
- Exploit idea: `accrue-collateral-asset` maps a ztoken id to a vault id through a chain of `is-eq` tests that falls through to the u100 sentinel. Reach it through `repay` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Snapshot every state variable `accrue-collateral-asset` touches, run `repay` with `amount`, including far above the real debt (the capping path), recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
