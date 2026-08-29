# Q5268: normalize-pyth via liquidate: record a repayment larger than the value actually delivere

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls which collateral and debt asset pair is targeted reach `normalize-pyth` (mainnet/contracts/market/v0-4-market.clar:297) in a state where it record a repayment larger than the value actually delivered? Given that it computes `adj` as `(+ expo 8)`, uses an `asserts!` as an early return when `adj` is zero, and converts a signed `int` price with `to-uint`, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:297` -> `normalize-pyth`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: which collateral and debt asset pair is targeted
- Exploit idea: `normalize-pyth` computes `adj` as `(+ expo 8)`, uses an `asserts!` as an early return when `adj` is zero, and converts a signed `int` price with `to-uint`. Reach it through `liquidate` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz which collateral and debt asset pair is targeted across its boundary values through `liquidate` in simnet and assert `normalize-pyth` never returns a value that breaks the invariant.
