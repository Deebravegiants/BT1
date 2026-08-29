# Q4280: oracle-price-legal via borrow: mint shares whose backing was never received

## Question
Does `borrow` (mainnet/contracts/market/v0-4-market.clar:1238) let an unprivileged attacker who controls the order of accrual versus price resolution inside the let reach `oracle-price-legal` (mainnet/contracts/market/v0-4-market.clar:362) in a state where it mint shares whose backing was never received? Given that it accepts any price strictly greater than zero, with no upper bound and no sanity band, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is protocol insolvency through uncollateralised debt.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:362` -> `oracle-price-legal`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the order of accrual versus price resolution inside the let
- Exploit idea: `oracle-price-legal` accepts any price strictly greater than zero, with no upper bound and no sanity band. Reach it through `borrow` and mint shares whose backing was never received.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Write a Clarinet simnet test calling `borrow` twice with the order of accrual versus price resolution inside the let varied, and assert that the value `oracle-price-legal` returns is identical in both runs; a divergence confirms the finding.
