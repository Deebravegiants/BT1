# Q2527: system-borrow via repay: destroy value through a truncation the opposite operation 

## Question
`system-borrow` (mainnet/contracts/vault/v0-vault-stx.clar:865) independently computes `scaled-amount` with `mul-div-up` from its own `index`, duplicating the market's own scaling of the same borrow. Can an unprivileged caller of `repay` (mainnet/contracts/market/v0-4-market.clar:1316), by choosing `amount`, including far above the real debt (the capping path), use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that value leaving a call equals value entering plus value minted minus value burned and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:865` -> `system-borrow`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `amount`, including far above the real debt (the capping path)
- Exploit idea: `system-borrow` independently computes `scaled-amount` with `mul-div-up` from its own `index`, duplicating the market's own scaling of the same borrow. Reach it through `repay` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `repay` with `amount`, including far above the real debt (the capping path), then read `system-borrow` state before and after in the same block and assert the two sides of the invariant are equal.
