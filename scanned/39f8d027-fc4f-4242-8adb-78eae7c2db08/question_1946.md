# Q1946: get-full-position via liquidate: record a repayment larger than the value actually delivere

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `min-collateral-expected`, can an unprivileged attacker make `get-full-position` (mainnet/contracts/market/v0-4-market.clar:470) record a repayment larger than the value actually delivered? `get-full-position` returns all collateral rows regardless of the enabled bitmap, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding protocol insolvency.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:470` -> `get-full-position`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `min-collateral-expected`
- Exploit idea: `get-full-position` returns all collateral rows regardless of the enabled bitmap. Reach it through `liquidate` and record a repayment larger than the value actually delivered.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with `min-collateral-expected` varied, and assert that the value `get-full-position` returns is identical in both runs; a divergence confirms the finding.
