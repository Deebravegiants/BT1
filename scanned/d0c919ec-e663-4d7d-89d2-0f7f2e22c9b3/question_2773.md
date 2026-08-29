# Q2773: collateral-remove via collateral-remove-redeem: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `collateral-remove-redeem` (mainnet/contracts/market/v0-4-market.clar:1211), controlling remaining zToken collateral whose price moves with the redeem, drive `collateral-remove` (mainnet/contracts/market/v0-market-vault.clar:406) — which decrements the map and writes the entry before `send-tokens` executes — to mint shares whose backing was never received, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:406` -> `collateral-remove`
- Entrypoint: `collateral-remove-redeem` (`mainnet/contracts/market/v0-4-market.clar:1211`), unprivileged and publicly callable
- Attacker controls: remaining zToken collateral whose price moves with the redeem
- Exploit idea: `collateral-remove` decrements the map and writes the entry before `send-tokens` executes. Reach it through `collateral-remove-redeem` and mint shares whose backing was never received.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `collateral-remove-redeem` with remaining zToken collateral whose price moves with the redeem, then read `collateral-remove` state before and after in the same block and assert the two sides of the invariant are equal.
