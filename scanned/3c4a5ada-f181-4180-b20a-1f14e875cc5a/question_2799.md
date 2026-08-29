# Q2799: accrue-collateral-asset via borrow: destroy value through a truncation the opposite operation 

## Question
`accrue-collateral-asset` (mainnet/contracts/market/v0-4-market.clar:273) maps a ztoken id to a vault id through a chain of `is-eq` tests that falls through to the u100 sentinel. Can an unprivileged caller of `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), by choosing the future mask produced by the new debt bit, use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that value leaving a call equals value entering plus value minted minus value burned and producing temporary freezing of funds?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:273` -> `accrue-collateral-asset`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the future mask produced by the new debt bit
- Exploit idea: `accrue-collateral-asset` maps a ztoken id to a vault id through a chain of `is-eq` tests that falls through to the u100 sentinel. Reach it through `borrow` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Snapshot every state variable `accrue-collateral-asset` touches, run `borrow` with the future mask produced by the new debt bit, recompute the invariant off-chain from the snapshot, and assert it matches the on-chain result.
