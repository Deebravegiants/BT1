# Q2357: price-multi-resolve via liquidate: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `liquidate` (mainnet/contracts/market/v0-4-market.clar:1382), controlling `borrower`, any third-party principal, drive `price-multi-resolve` (mainnet/contracts/market/v0-4-market.clar:397) — which folds `iter-price-multi` into a POSITIONAL price list, asserting only the `valid` flag at the end — to mint shares whose backing was never received, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause protocol insolvency through uncollateralised debt?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:397` -> `price-multi-resolve`
- Entrypoint: `liquidate` (`mainnet/contracts/market/v0-4-market.clar:1382`), unprivileged and publicly callable
- Attacker controls: `borrower`, any third-party principal
- Exploit idea: `price-multi-resolve` folds `iter-price-multi` into a POSITIONAL price list, asserting only the `valid` flag at the end. Reach it through `liquidate` and mint shares whose backing was never received.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency through uncollateralised debt
- Fast validation: Run the baseline `liquidate` call, then the attacker-shaped one with `borrower`, any third-party principal, and assert the attacker's net token balance change is zero or negative.
