# Q4172: calculate-asset-notional-value via supply-collateral-add: mint shares whose backing was never received

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls `amount` reach `calculate-asset-notional-value` (mainnet/contracts/market/v0-4-market.clar:544) in a state where it mint shares whose backing was never received? Given that it normalizes collateral with round-down and debt with round-up, and calls `accrue-and-cache` with `unwrap-panic` inside the fold, the invariant that every round-up has a paired round-down that repetition cannot exploit breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:544` -> `calculate-asset-notional-value`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `calculate-asset-notional-value` normalizes collateral with round-down and debt with round-up, and calls `accrue-and-cache` with `unwrap-panic` inside the fold. Reach it through `supply-collateral-add` and mint shares whose backing was never received.
- Invariant to test: every round-up has a paired round-down that repetition cannot exploit
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `supply-collateral-add` twice with `amount` varied, and assert that the value `calculate-asset-notional-value` returns is identical in both runs; a divergence confirms the finding.
