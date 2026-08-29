# Q5408: send-tokens via liquidate: record a repayment larger than the value actually delivere

## Question
Does `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) let an unprivileged attacker who controls `borrower`, any third-party principal reach `send-tokens` (mainnet/contracts/market/v0-market-vault.clar:259) in a state where it record a repayment larger than the value actually delivered? Given that it pushes an asset to a caller-chosen recipient principal, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:259` -> `send-tokens`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `borrower`, any third-party principal
- Exploit idea: `send-tokens` pushes an asset to a caller-chosen recipient principal. Reach it through `liquidate` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with `borrower`, any third-party principal varied, and assert that the value `send-tokens` returns is identical in both runs; a divergence confirms the finding.
