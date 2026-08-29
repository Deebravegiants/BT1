# Q5588: find-asset via borrow: record a repayment larger than the value actually delivere

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls `amount` reach `find-asset` (mainnet/contracts/market/v0-4-market.clar:584) in a state where it record a repayment larger than the value actually delivered? Given that it returns `none` when the id is absent, and several callers resolve that with `unwrap-panic`, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:584` -> `find-asset`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `find-asset` returns `none` when the id is absent, and several callers resolve that with `unwrap-panic`. Reach it through `borrow` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with `amount` varied, and assert that the value `find-asset` returns is identical in both runs; a divergence confirms the finding.
