# Q1188: accrue-collateral-asset via collateral-add: count one deposit as backing for two simultaneous claims

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls the `ft` trait principal reach `accrue-collateral-asset` (mainnet/contracts/market/v0-4-market.clar:273) in a state where it count one deposit as backing for two simultaneous claims? Given that it maps a ztoken id to a vault id through a chain of `is-eq` tests that falls through to the u100 sentinel, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is temporary freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:273` -> `accrue-collateral-asset`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `accrue-collateral-asset` maps a ztoken id to a vault id through a chain of `is-eq` tests that falls through to the u100 sentinel. Reach it through `collateral-add` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - temporary freezing of funds
- Fast validation: Fuzz the `ft` trait principal across its boundary values through `collateral-add` in simnet and assert `accrue-collateral-asset` never returns a value that breaks the invariant.
