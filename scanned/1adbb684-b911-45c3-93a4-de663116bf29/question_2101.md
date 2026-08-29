# Q2101: increment via liquidate-redeem: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `liquidate-redeem` (mainnet/contracts/market/v0-4-market.clar:1604), controlling the vault whose share price the redemption moves, drive `increment` (mainnet/contracts/market/v0-market-vault.clar:137) — which advances the user-id nonce — to mint shares whose backing was never received, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause direct theft of another user's collateral?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:137` -> `increment`
- Entrypoint: `liquidate-redeem` (`mainnet/contracts/market/v0-4-market.clar:1604`), unprivileged and publicly callable
- Attacker controls: the vault whose share price the redemption moves
- Exploit idea: `increment` advances the user-id nonce. Reach it through `liquidate-redeem` and mint shares whose backing was never received.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of another user's collateral
- Fast validation: In `local-testing/tests` on a local fork, drive `liquidate-redeem` with the vault whose share price the redemption moves, then read `increment` state before and after in the same block and assert the two sides of the invariant are equal.
