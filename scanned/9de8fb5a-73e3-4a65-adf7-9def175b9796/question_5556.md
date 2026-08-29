# Q5556: check-confidence via collateral-remove-redeem: record a repayment larger than the value actually delivere

## Question
Does `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211) let an unprivileged attacker who controls `amount` used for BOTH the collateral removal and the share redemption reach `check-confidence` (mainnet/contracts/market/v0-4-market.clar:305) in a state where it record a repayment larger than the value actually delivered? Given that it compares the Pyth confidence interval against `max-confidence-ratio` in BPS, a gate that has no DIA equivalent, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is permanent freezing of funds.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:305` -> `check-confidence`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: `amount` used for BOTH the collateral removal and the share redemption
- Exploit idea: `check-confidence` compares the Pyth confidence interval against `max-confidence-ratio` in BPS, a gate that has no DIA equivalent. Reach it through `collateral-remove-redeem` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - permanent freezing of funds
- Fast validation: Fuzz `amount` used for BOTH the collateral removal and the share redemption across its boundary values through `collateral-remove-redeem` in simnet and assert `check-confidence` never returns a value that breaks the invariant.
