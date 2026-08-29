# Q1784: accrue-and-cache via collateral-remove-redeem: count one deposit as backing for two simultaneous claims

## Question
Does `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) let an unprivileged attacker who controls remaining zToken collateral whose price moves with the redeem reach `accrue-and-cache` (mainnet/contracts/market/v0-4-market.clar:245) in a state where it count one deposit as backing for two simultaneous claims? Given that it keys `index-cache` on `{timestamp: stacks-block-time, aid}` and returns the cached record forever after, with no invalidation when the vault later moves, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:245` -> `accrue-and-cache`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: remaining zToken collateral whose price moves with the redeem
- Exploit idea: `accrue-and-cache` keys `index-cache` on `{timestamp: stacks-block-time, aid}` and returns the cached record forever after, with no invalidation when the vault later moves. Reach it through `collateral-remove-redeem` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-remove-redeem` twice with remaining zToken collateral whose price moves with the redeem varied, and assert that the value `accrue-and-cache` returns is identical in both runs; a divergence confirms the finding.
