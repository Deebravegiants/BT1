# Q5204: convert-to-scaled-debt via liquidate-multi: record a repayment larger than the value actually delivere

## Question
Does `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593) let an unprivileged attacker who controls the full batch list and its ordering reach `convert-to-scaled-debt` (mainnet/contracts/market/v0-4-market.clar:648) in a state where it record a repayment larger than the value actually delivered? Given that it scales a token amount by the cached borrow index, rounding up on the borrow path, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:648` -> `convert-to-scaled-debt`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: the full batch list and its ordering
- Exploit idea: `convert-to-scaled-debt` scales a token amount by the cached borrow index, rounding up on the borrow path. Reach it through `liquidate-multi` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate-multi` twice with the full batch list and its ordering varied, and assert that the value `convert-to-scaled-debt` returns is identical in both runs; a divergence confirms the finding.
