# Q5244: mask-to-list-internal via liquidate: record a repayment larger than the value actually delivere

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls which collateral and debt asset pair is targeted reach `mask-to-list-internal` (mainnet/contracts/market/v0-4-market.clar:435) in a state where it record a repayment larger than the value actually delivered? Given that it expands mask bits into a list bounded at 64 entries, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:435` -> `mask-to-list-internal`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: which collateral and debt asset pair is targeted
- Exploit idea: `mask-to-list-internal` expands mask bits into a list bounded at 64 entries. Reach it through `liquidate` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz which collateral and debt asset pair is targeted across its boundary values through `liquidate` in simnet and assert `mask-to-list-internal` never returns a value that breaks the invariant.
