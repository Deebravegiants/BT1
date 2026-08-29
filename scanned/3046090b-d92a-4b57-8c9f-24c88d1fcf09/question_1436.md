# Q1436: accrue-user-debts via call-ststx-ratio: count one deposit as backing for two simultaneous claims

## Question
Does `call-ststx-ratio` (mainnet/contracts/market/v0-4-market.clar:1015) let an unprivileged attacker who controls the block and transaction position at which the external ratio is fetched reach `accrue-user-debts` (mainnet/contracts/market/v0-4-market.clar:259) in a state where it count one deposit as backing for two simultaneous claims? Given that it folds accrual over the position's debt list only, the invariant that shares outstanding valued at the current share price never exceed `total-assets` breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:259` -> `accrue-user-debts`
- Entrypoint: `call-ststx-ratio` (`mainnet/contracts/market/v0-4-market.clar:1015`), unprivileged and publicly callable
- Attacker controls: the block and transaction position at which the external ratio is fetched
- Exploit idea: `accrue-user-debts` folds accrual over the position's debt list only. Reach it through `call-ststx-ratio` and count one deposit as backing for two simultaneous claims.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `call-ststx-ratio` twice with the block and transaction position at which the external ratio is fetched varied, and assert that the value `accrue-user-debts` returns is identical in both runs; a divergence confirms the finding.
