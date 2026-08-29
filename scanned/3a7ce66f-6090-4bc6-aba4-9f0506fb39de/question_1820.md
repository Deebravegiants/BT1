# Q1820: accrue-collateral-asset via borrow: count one deposit as backing for two simultaneous claims

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls the `ft` trait principal reach `accrue-collateral-asset` (mainnet/contracts/market/v0-4-market.clar:273) in a state where it count one deposit as backing for two simultaneous claims? Given that it maps a ztoken id to a vault id through a chain of `is-eq` tests that falls through to the u100 sentinel, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:273` -> `accrue-collateral-asset`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `accrue-collateral-asset` maps a ztoken id to a vault id through a chain of `is-eq` tests that falls through to the u100 sentinel. Reach it through `borrow` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with the `ft` trait principal varied, and assert that the value `accrue-collateral-asset` returns is identical in both runs; a divergence confirms the finding.
