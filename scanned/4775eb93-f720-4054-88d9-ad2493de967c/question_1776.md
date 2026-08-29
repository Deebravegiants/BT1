# Q1776: accrue-collateral-asset via collateral-remove-redeem: count one deposit as backing for two simultaneous claims

## Question
Does `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) let an unprivileged attacker who controls `min-underlying` reach `accrue-collateral-asset` (mainnet/contracts/market/v0-4-market.clar:273) in a state where it count one deposit as backing for two simultaneous claims? Given that it maps a ztoken id to a vault id through a chain of `is-eq` tests that falls through to the u100 sentinel, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:273` -> `accrue-collateral-asset`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `min-underlying`
- Exploit idea: `accrue-collateral-asset` maps a ztoken id to a vault id through a chain of `is-eq` tests that falls through to the u100 sentinel. Reach it through `collateral-remove-redeem` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `min-underlying` across its boundary values through `collateral-remove-redeem` in simnet and assert `accrue-collateral-asset` never returns a value that breaks the invariant.
