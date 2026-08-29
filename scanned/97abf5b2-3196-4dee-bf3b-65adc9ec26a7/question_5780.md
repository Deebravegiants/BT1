# Q5780: mask-pos via liquidate-multi: record a repayment larger than the value actually delivere

## Question
Does `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) let an unprivileged attacker who controls the full batch list and its ordering reach `mask-pos` (mainnet/contracts/market/v0-market-vault.clar:91) in a state where it record a repayment larger than the value actually delivered? Given that it maps an asset id to a bit position, offsetting debt bits by DEBT-OFFSET, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:91` -> `mask-pos`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the full batch list and its ordering
- Exploit idea: `mask-pos` maps an asset id to a bit position, offsetting debt bits by DEBT-OFFSET. Reach it through `liquidate-multi` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate-multi` twice with the full batch list and its ordering varied, and assert that the value `mask-pos` returns is identical in both runs; a divergence confirms the finding.
