# Q2393: price-multi-resolve via supply-collateral-add: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), controlling the position state the final collateral-add is validated against, drive `price-multi-resolve` (mainnet/contracts/market/v0-4-market.clar:397) — which folds `iter-price-multi` into a POSITIONAL price list, asserting only the `valid` flag at the end — to mint shares whose backing was never received, breaking the invariant that shares outstanding valued at the current share price never exceed `total-assets`, and cause protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:397` -> `price-multi-resolve`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the position state the final collateral-add is validated against
- Exploit idea: `price-multi-resolve` folds `iter-price-multi` into a POSITIONAL price list, asserting only the `valid` flag at the end. Reach it through `supply-collateral-add` and mint shares whose backing was never received.
- Invariant to test: shares outstanding valued at the current share price never exceed `total-assets`
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `supply-collateral-add` call, then the attacker-shaped one with the position state the final collateral-add is validated against, and assert the attacker's net token balance change is zero or negative.
