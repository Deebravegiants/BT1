# Q4328: find-debt-scaled via supply-collateral-add: mint shares whose backing was never received

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls `min-shares` (the only slippage bound on the deposit leg) reach `find-debt-scaled` (mainnet/contracts/market/v0-4-market.clar:621) in a state where it mint shares whose backing was never received? Given that it returns u0 for an absent asset, making a missing debt row indistinguishable from no debt, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is permanent freezing of unclaimed yield.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:621` -> `find-debt-scaled`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `min-shares` (the only slippage bound on the deposit leg)
- Exploit idea: `find-debt-scaled` returns u0 for an absent asset, making a missing debt row indistinguishable from no debt. Reach it through `supply-collateral-add` and mint shares whose backing was never received.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Write a Clarinet simnet test calling `supply-collateral-add` twice with `min-shares` (the only slippage bound on the deposit leg) varied, and assert that the value `find-debt-scaled` returns is identical in both runs; a divergence confirms the finding.
