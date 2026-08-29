# Q2375: convert-to-scaled-debt via supply-collateral-add: destroy value through a truncation the opposite operation 

## Question
`convert-to-scaled-debt` (mainnet/contracts/market/v0-4-market.clar:648) scales a token amount by the cached borrow index, rounding up on the borrow path. Can an unprivileged caller of `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), by choosing `min-shares` (the only slippage bound on the deposit leg), use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that value leaving a call equals value entering plus value minted minus value burned and producing protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:648` -> `convert-to-scaled-debt`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `min-shares` (the only slippage bound on the deposit leg)
- Exploit idea: `convert-to-scaled-debt` scales a token amount by the cached borrow index, rounding up on the borrow path. Reach it through `supply-collateral-add` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `supply-collateral-add` call, then the attacker-shaped one with `min-shares` (the only slippage bound on the deposit leg), and assert the attacker's net token balance change is zero or negative.
