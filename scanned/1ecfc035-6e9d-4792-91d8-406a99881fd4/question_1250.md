# Q1250: get-position via borrow: record a repayment larger than the value actually delivere

## Question
Entering through `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) while controlling the `ft` trait principal, can an unprivileged attacker make `get-position` (mainnet/contracts/market/v0-4-market.clar:466) record a repayment larger than the value actually delivered? `get-position` returns only rows whose bit is set in the ENABLED bitmap, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:466` -> `get-position`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `get-position` returns only rows whose bit is set in the ENABLED bitmap. Reach it through `borrow` and record a repayment larger than the value actually delivered.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with the `ft` trait principal varied, and assert that the value `get-position` returns is identical in both runs; a divergence confirms the finding.
