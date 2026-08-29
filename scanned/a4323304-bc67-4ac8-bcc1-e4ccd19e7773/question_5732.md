# Q5732: calc-index-next via liquidate: record a repayment larger than the value actually delivere

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `borrower`, any third-party principal reach `calc-index-next` (mainnet/contracts/vault/v0-vault-stx.clar:183) in a state where it record a repayment larger than the value actually delivered? Given that it applies a multiplier to the current index, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:183` -> `calc-index-next`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `borrower`, any third-party principal
- Exploit idea: `calc-index-next` applies a multiplier to the current index. Reach it through `liquidate` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with `borrower`, any third-party principal varied, and assert that the value `calc-index-next` returns is identical in both runs; a divergence confirms the finding.
