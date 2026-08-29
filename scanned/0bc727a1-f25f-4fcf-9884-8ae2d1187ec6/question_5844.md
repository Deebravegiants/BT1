# Q5844: calc-liq-debt-repay-real via liquidate: record a repayment larger than the value actually delivere

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls which collateral and debt asset pair is targeted reach `calc-liq-debt-repay-real` (mainnet/contracts/market/v0-4-market.clar:733) in a state where it record a repayment larger than the value actually delivered? Given that it re-derives debt from capped collateral by dividing by `(+ BPS liq-penalty)`, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:733` -> `calc-liq-debt-repay-real`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: which collateral and debt asset pair is targeted
- Exploit idea: `calc-liq-debt-repay-real` re-derives debt from capped collateral by dividing by `(+ BPS liq-penalty)`. Reach it through `liquidate` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz which collateral and debt asset pair is targeted across its boundary values through `liquidate` in simnet and assert `calc-liq-debt-repay-real` never returns a value that breaks the invariant.
