# Q4988: remove-user-collateral via collateral-remove: record a repayment larger than the value actually delivere

## Question
Does `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107) let an unprivileged attacker who controls `amount` relative to the current collateral row (the removing-all branch) reach `remove-user-collateral` (mainnet/contracts/market/v0-market-vault.clar:205) in a state where it record a repayment larger than the value actually delivered? Given that it asserts sufficiency then `map-delete`s only on an exact zero, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:205` -> `remove-user-collateral`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: `amount` relative to the current collateral row (the removing-all branch)
- Exploit idea: `remove-user-collateral` asserts sufficiency then `map-delete`s only on an exact zero. Reach it through `collateral-remove` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `collateral-remove` twice with `amount` relative to the current collateral row (the removing-all branch) varied, and assert that the value `remove-user-collateral` returns is identical in both runs; a divergence confirms the finding.
