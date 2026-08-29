# Q1920: write-feeds via supply-collateral-add: count one deposit as backing for two simultaneous claims

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls `amount` reach `write-feeds` (mainnet/contracts/market/v0-4-market.clar:149) in a state where it count one deposit as backing for two simultaneous claims? Given that it folds up to three attacker-supplied buffers through `write-feed` with a `(response bool uint)` accumulator, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:149` -> `write-feeds`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `write-feeds` folds up to three attacker-supplied buffers through `write-feed` with a `(response bool uint)` accumulator. Reach it through `supply-collateral-add` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `amount` across its boundary values through `supply-collateral-add` in simnet and assert `write-feeds` never returns a value that breaks the invariant.
