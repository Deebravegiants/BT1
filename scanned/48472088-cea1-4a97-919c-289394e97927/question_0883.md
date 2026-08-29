# Q0883: send-tokens via supply-collateral-add: have the same quantity scaled twice by two contracts that 

## Question
`send-tokens` (mainnet/contracts/market/v0-market-vault.clar:259) pushes an asset to a caller-chosen recipient principal. Can an unprivileged caller of `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), by choosing the `ft` trait principal deciding which vault is routed to, use that to have the same quantity scaled twice by two contracts that round differently, violating the invariant that interest charged to borrowers equals interest distributed to suppliers plus treasury and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:259` -> `send-tokens`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: the `ft` trait principal deciding which vault is routed to
- Exploit idea: `send-tokens` pushes an asset to a caller-chosen recipient principal. Reach it through `supply-collateral-add` and have the same quantity scaled twice by two contracts that round differently.
- Invariant to test: interest charged to borrowers equals interest distributed to suppliers plus treasury
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `supply-collateral-add` with the `ft` trait principal deciding which vault is routed to, then read `send-tokens` state before and after in the same block and assert the two sides of the invariant are equal.
