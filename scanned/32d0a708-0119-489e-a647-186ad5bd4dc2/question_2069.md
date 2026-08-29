# Q2069: send-tokens via repay: mint shares whose backing was never received

## Question
Can an unprivileged attacker entering through `repay` (mainnet/contracts/market/v0-4-market.clar:1316), controlling the `ft` trait principal, drive `send-tokens` (mainnet/contracts/market/v0-market-vault.clar:259) — which pushes an asset to a caller-chosen recipient principal — to mint shares whose backing was never received, breaking the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury, and cause permanent freezing of unclaimed yield?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:259` -> `send-tokens`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal
- Exploit idea: `send-tokens` pushes an asset to a caller-chosen recipient principal. Reach it through `repay` and mint shares whose backing was never received.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: High - permanent freezing of unclaimed yield
- Fast validation: Run the baseline `repay` call, then the attacker-shaped one with the `ft` trait principal, and assert the attacker's net token balance change is zero or negative.
