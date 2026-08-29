# Q1718: get-position via collateral-add: record a repayment larger than the value actually delivere

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling the three `price-feeds` buffers and their order, can an unprivileged attacker make `get-position` (mainnet/contracts/market/v0-4-market.clar:466) record a repayment larger than the value actually delivered? `get-position` returns only rows whose bit is set in the ENABLED bitmap, so the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` would fail, yielding permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:466` -> `get-position`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the three `price-feeds` buffers and their order
- Exploit idea: `get-position` returns only rows whose bit is set in the ENABLED bitmap. Reach it through `collateral-add` and record a repayment larger than the value actually delivered.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `collateral-add` twice with the three `price-feeds` buffers and their order varied, and assert that the value `get-position` returns is identical in both runs; a divergence confirms the finding.
