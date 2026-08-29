# Q1256: iter-price-multi via call-ststx-ratio: count one deposit as backing for two simultaneous claims

## Question
Does `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015) let an unprivileged attacker who controls the block and transaction position at which the external ratio is fetched reach `iter-price-multi` (mainnet/contracts/market/v0-4-market.clar:405) in a state where it count one deposit as backing for two simultaneous claims? Given that it carries `aids` and `idx` in its accumulator but never uses them to align prices with asset ids, and appends under `as-max-len? ... u64`, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:405` -> `iter-price-multi`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: the block and transaction position at which the external ratio is fetched
- Exploit idea: `iter-price-multi` carries `aids` and `idx` in its accumulator but never uses them to align prices with asset ids, and appends under `as-max-len? ... u64`. Reach it through `call-ststx-ratio` and count one deposit as backing for two simultaneous claims.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `call-ststx-ratio` twice with the block and transaction position at which the external ratio is fetched varied, and assert that the value `iter-price-multi` returns is identical in both runs; a divergence confirms the finding.
