# Q1736: accrue-debt-asset via collateral-add: count one deposit as backing for two simultaneous claims

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls the three `price-feeds` buffers and their order reach `accrue-debt-asset` (mainnet/contracts/market/v0-4-market.clar:262) in a state where it count one deposit as backing for two simultaneous claims? Given that it calls `accrue-and-cache` with `unwrap-panic` inside a fold whose accumulator ignores the result, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:262` -> `accrue-debt-asset`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the three `price-feeds` buffers and their order
- Exploit idea: `accrue-debt-asset` calls `accrue-and-cache` with `unwrap-panic` inside a fold whose accumulator ignores the result. Reach it through `collateral-add` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-add` twice with the three `price-feeds` buffers and their order varied, and assert that the value `accrue-debt-asset` returns is identical in both runs; a divergence confirms the finding.
