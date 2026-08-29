# Q2245: status via collateral-remove: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `collateral-remove` (mainnet/contracts/market/v0-4-market.clar:1107), controlling the `ft` trait principal, drive `status` (mainnet/contracts/registry/v0-assets.clar:115) — which derives `collateral` and `debt` flags from bit tests against whatever mask it was handed — to mint shares whose backing was never received, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/registry/v0-assets.clar:115` -> `status`
- Entrypoint: `collateral-remove` (`mainnet/contracts/market/v0-4-market.clar:1107`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `status` derives `collateral` and `debt` flags from bit tests against whatever mask it was handed. Reach it through `collateral-remove` and mint shares whose backing was never received.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-remove` with the `ft` trait principal, then read `status` state before and after in the same block and assert the two sides of the invariant are equal.
