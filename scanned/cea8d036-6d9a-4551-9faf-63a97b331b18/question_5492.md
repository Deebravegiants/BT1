# Q5492: zip via deposit: record a repayment larger than the value actually delivere

## Question
Does `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) let an unprivileged attacker who controls `min-out` reach `zip` (mainnet/contracts/vault/v0-vault-stx.clar:226) in a state where it record a repayment larger than the value actually delivered? Given that it pairs the utilization and rate point lists element by element, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:226` -> `zip`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `min-out`
- Exploit idea: `zip` pairs the utilization and rate point lists element by element. Reach it through `deposit` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `deposit` twice with `min-out` varied, and assert that the value `zip` returns is identical in both runs; a divergence confirms the finding.
