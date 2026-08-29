# Q5216: send-underlying via deposit: record a repayment larger than the value actually delivere

## Question
Does `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763) let an unprivileged attacker who controls `amount` reach `send-underlying` (mainnet/contracts/vault/v0-vault-stx.clar:296) in a state where it record a repayment larger than the value actually delivered? Given that it pushes the underlying under an `as-contract?` post-condition scope, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:296` -> `send-underlying`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `send-underlying` pushes the underlying under an `as-contract?` post-condition scope. Reach it through `deposit` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `deposit` twice with `amount` varied, and assert that the value `send-underlying` returns is identical in both runs; a divergence confirms the finding.
