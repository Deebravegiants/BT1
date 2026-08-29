# Q5648: check-confidence via call-ststx-ratio: record a repayment larger than the value actually delivere

## Question
Does `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015) let an unprivileged attacker who controls the block and transaction position at which the external ratio is fetched reach `check-confidence` (mainnet/contracts/market/v0-4-market.clar:305) in a state where it record a repayment larger than the value actually delivered? Given that it compares the Pyth confidence interval against `max-confidence-ratio` in BPS, a gate that has no DIA equivalent, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:305` -> `check-confidence`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: the block and transaction position at which the external ratio is fetched
- Exploit idea: `check-confidence` compares the Pyth confidence interval against `max-confidence-ratio` in BPS, a gate that has no DIA equivalent. Reach it through `call-ststx-ratio` and record a repayment larger than the value actually delivered.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `call-ststx-ratio` twice with the block and transaction position at which the external ratio is fetched varied, and assert that the value `check-confidence` returns is identical in both runs; a divergence confirms the finding.
