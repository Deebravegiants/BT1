# Q1448: price-multi-resolve via collateral-add: count one deposit as backing for two simultaneous claims

## Question
Does `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) let an unprivileged attacker who controls the three `price-feeds` buffers and their order reach `price-multi-resolve` (mainnet/contracts/market/v0-4-market.clar:397) in a state where it count one deposit as backing for two simultaneous claims? Given that it folds `iter-price-multi` into a POSITIONAL price list, asserting only the `valid` flag at the end, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:397` -> `price-multi-resolve`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the three `price-feeds` buffers and their order
- Exploit idea: `price-multi-resolve` folds `iter-price-multi` into a POSITIONAL price list, asserting only the `valid` flag at the end. Reach it through `collateral-add` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `collateral-add` twice with the three `price-feeds` buffers and their order varied, and assert that the value `price-multi-resolve` returns is identical in both runs; a divergence confirms the finding.
