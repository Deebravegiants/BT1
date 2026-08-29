# Q2869: find-asset via liquidate-multi: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `liquidate-multi` (mainnet/contracts/market/v0-4-market.clar:1593), controlling which borrowers are placed early versus late in the batch, drive `find-asset` (mainnet/contracts/market/v0-4-market.clar:584) — which returns `none` when the id is absent, and several callers resolve that with `unwrap-panic` — to mint shares whose backing was never received, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause theft of unclaimed yield?

## Target
- File/function: `mainnet/contracts/market/v0-4-market.clar:584` -> `find-asset`
- Entrypoint: `liquidate-multi` (`mainnet/contracts/market/v0-4-market.clar:1593`), unprivileged and publicly callable
- Attacker controls: which borrowers are placed early versus late in the batch
- Exploit idea: `find-asset` returns `none` when the id is absent, and several callers resolve that with `unwrap-panic`. Reach it through `liquidate-multi` and mint shares whose backing was never received.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate-multi` with which borrowers are placed early versus late in the batch, then read `find-asset` state before and after in the same block and assert the two sides of the invariant are equal.
