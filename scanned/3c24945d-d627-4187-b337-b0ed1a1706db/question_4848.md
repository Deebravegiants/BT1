# Q4848: normalize-pyth via supply-collateral-add: mint shares whose backing was never received

## Question
Does `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175) let an unprivileged attacker who controls `min-shares` (the only slippage bound on the deposit leg) reach `normalize-pyth` (mainnet/contracts/market/v0-4-market.clar:297) in a state where it mint shares whose backing was never received? Given that it computes `adj` as `(+ expo 8)`, uses an `asserts!` as an early return when `adj` is zero, and converts a signed `int` price with `to-uint`, the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset breaks and the result is permanent freezing of a position that can never be closed.

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:297` -> `normalize-pyth`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `min-shares` (the only slippage bound on the deposit leg)
- Exploit idea: `normalize-pyth` computes `adj` as `(+ expo 8)`, uses an `asserts!` as an early return when `adj` is zero, and converts a signed `int` price with `to-uint`. Reach it through `supply-collateral-add` and mint shares whose backing was never received.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - permanent freezing of a position that can never be closed
- Fast validation: Fuzz `min-shares` (the only slippage bound on the deposit leg) across its boundary values through `supply-collateral-add` in simnet and assert `normalize-pyth` never returns a value that breaks the invariant.
