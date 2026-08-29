# Q4952: find-superset via borrow: record a repayment larger than the value actually delivere

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls `amount` reach `find-superset` (mainnet/contracts/registry/v0-egroup.clar:262) in a state where it record a repayment larger than the value actually delivered? Given that it returns the FIRST mask that is a superset, walking buckets in population order rather than finding the tightest, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is protocol insolvency.

## Target
- File/function: `mainnet/contracts/registry/v0-egroup.clar:262` -> `find-superset`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `find-superset` returns the FIRST mask that is a superset, walking buckets in population order rather than finding the tightest. Reach it through `borrow` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with `amount` varied, and assert that the value `find-superset` returns is identical in both runs; a divergence confirms the finding.
