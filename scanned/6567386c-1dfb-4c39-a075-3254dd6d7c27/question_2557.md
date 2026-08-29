# Q2557: mask-pos via collateral-remove-redeem: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), controlling the zToken/underlying id mapping reached (the u100 sentinel branch), drive `mask-pos` (mainnet/contracts/market/v0-market-vault.clar:91) — which maps an asset id to a bit position, offsetting debt bits by DEBT-OFFSET — to mint shares whose backing was never received, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:91` -> `mask-pos`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: the zToken/underlying id mapping reached (the u100 sentinel branch)
- Exploit idea: `mask-pos` maps an asset id to a bit position, offsetting debt bits by DEBT-OFFSET. Reach it through `collateral-remove-redeem` and mint shares whose backing was never received.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-remove-redeem` with the zToken/underlying id mapping reached (the u100 sentinel branch), then read `mask-pos` state before and after in the same block and assert the two sides of the invariant are equal.
