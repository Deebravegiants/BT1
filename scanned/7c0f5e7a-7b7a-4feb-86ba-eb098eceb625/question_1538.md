# Q1538: oracle-last-update via liquidate: record a repayment larger than the value actually delivere

## Question
Entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382) while controlling `min-collateral-expected`, can an unprivileged attacker make `oracle-last-update` (mainnet/contracts/market/v0-4-market.clar:939) record a repayment larger than the value actually delivered? `oracle-last-update` returns the stored monotonic timestamp for a `{type, ident}` key shared by every asset using that feed, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:939` -> `oracle-last-update`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `min-collateral-expected`
- Exploit idea: `oracle-last-update` returns the stored monotonic timestamp for a `{type, ident}` key shared by every asset using that feed. Reach it through `liquidate` and record a repayment larger than the value actually delivered.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `liquidate` twice with `min-collateral-expected` varied, and assert that the value `oracle-last-update` returns is identical in both runs; a divergence confirms the finding.
