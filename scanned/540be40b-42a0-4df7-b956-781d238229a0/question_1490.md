# Q1490: find-and-resolve-asset-value via collateral-add: record a repayment larger than the value actually delivere

## Question
Entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020) while controlling the three `price-feeds` buffers and their order, can an unprivileged attacker make `find-and-resolve-asset-value` (mainnet/contracts/market/v0-4-market.clar:668) record a repayment larger than the value actually delivered? `find-and-resolve-asset-value` reuses an already-resolved price from the asset list and returns u0 when the asset is not found, so the invariant that value leaving a call equals value entering plus value minted minus value burned would fail, yielding protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:668` -> `find-and-resolve-asset-value`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the three `price-feeds` buffers and their order
- Exploit idea: `find-and-resolve-asset-value` reuses an already-resolved price from the asset list and returns u0 when the asset is not found. Reach it through `collateral-add` and record a repayment larger than the value actually delivered.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `collateral-add` twice with the three `price-feeds` buffers and their order varied, and assert that the value `find-and-resolve-asset-value` returns is identical in both runs; a divergence confirms the finding.
