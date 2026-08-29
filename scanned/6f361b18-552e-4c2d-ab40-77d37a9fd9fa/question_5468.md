# Q5468: send-underlying via accrue: record a repayment larger than the value actually delivere

## Question
Does `accrue` (mainnet/contracts/vault/v0-vault-stx.clar:835) let an unprivileged attacker who controls the block time at which accrual is first triggered in a block reach `send-underlying` (mainnet/contracts/vault/v0-vault-stx.clar:296) in a state where it record a repayment larger than the value actually delivered? Given that it pushes the underlying under an `as-contract?` post-condition scope, the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:296` -> `send-underlying`
- Entrypoint: `accrue` (`mainnet/contracts/vault/v0-vault-stx.clar:835`), unprivileged and publicly callable
- Attacker controls: the block time at which accrual is first triggered in a block
- Exploit idea: `send-underlying` pushes the underlying under an `as-contract?` post-condition scope. Reach it through `accrue` and record a repayment larger than the value actually delivered.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `accrue` twice with the block time at which accrual is first triggered in a block varied, and assert that the value `send-underlying` returns is identical in both runs; a divergence confirms the finding.
