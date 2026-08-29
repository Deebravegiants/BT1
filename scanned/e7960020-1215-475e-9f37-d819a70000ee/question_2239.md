# Q2239: mask-update via supply-collateral-add: destroy value through a truncation the opposite operation 

## Question
`mask-update` (mainnet/contracts/market/v0-market-vault.clar:94) sets or clears one bit, clearing only when the row reaches exactly zero. Can an unprivileged caller of `supply-collateral-add` (mainnet/contracts/market/v0-4-market.clar:1175), by choosing `amount`, use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that value leaving a call equals value entering plus value minted minus value burned and producing theft of unclaimed yield?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:94` -> `mask-update`
- Entrypoint: `supply-collateral-add` (`mainnet/contracts/market/v0-4-market.clar:1175`), unprivileged and publicly callable
- Attacker controls: `amount`
- Exploit idea: `mask-update` sets or clears one bit, clearing only when the row reaches exactly zero. Reach it through `supply-collateral-add` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: High - theft of unclaimed yield
- Fast validation: In `local-testing/tests` on a local fork, drive `supply-collateral-add` with `amount`, then read `mask-update` state before and after in the same block and assert the two sides of the invariant are equal.
