# Q1340: user-safe-mask via collateral-remove: count one deposit as backing for two simultaneous claims

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls the `ft` trait principal reach `user-safe-mask` (mainnet/contracts/market/v0-4-market.clar:428) in a state where it count one deposit as backing for two simultaneous claims? Given that it ANDs the user's collateral bits against the enabled bitmap but keeps ALL debt bits unfiltered, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:428` -> `user-safe-mask`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `user-safe-mask` ANDs the user's collateral bits against the enabled bitmap but keeps ALL debt bits unfiltered. Reach it through `collateral-remove` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `collateral-remove` twice with the `ft` trait principal varied, and assert that the value `user-safe-mask` returns is identical in both runs; a divergence confirms the finding.
