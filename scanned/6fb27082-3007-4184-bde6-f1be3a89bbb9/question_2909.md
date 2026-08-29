# Q2909: get-notional-evaluation via collateral-add: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `collateral-add` (mainnet/contracts/market/v0-4-market.clar:1020), controlling the `ft` trait principal, drive `get-notional-evaluation` (mainnet/contracts/market/v0-4-market.clar:514) — which folds over the ENABLED asset list, so a position row whose asset is absent from that list contributes nothing to either total — to mint shares whose backing was never received, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause protocol insolvency?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:514` -> `get-notional-evaluation`
- Entrypoint: `collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1020`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `get-notional-evaluation` folds over the ENABLED asset list, so a position row whose asset is absent from that list contributes nothing to either total. Reach it through `collateral-add` and mint shares whose backing was never received.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - protocol insolvency
- Fast validation: Run the baseline `collateral-add` call, then the attacker-shaped one with the `ft` trait principal, and assert the attacker's net token balance change is zero or negative.
