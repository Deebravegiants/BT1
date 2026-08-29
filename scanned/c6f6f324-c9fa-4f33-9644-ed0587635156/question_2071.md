# Q2071: socialize-debt via repay: destroy value through a truncation the opposite operation 

## Question
`socialize-debt` (mainnet/contracts/vault/v0-vault-stx.clar:944) writes down `lindex` by one ratio while reducing `assets` by a completely different `principal-reduction`. Can an unprivileged caller of `repay` (mainnet/contracts/market/v0-4-market.clar:1316), by choosing `amount`, including far above the real debt (the capping path), use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that value leaving a call equals value entering plus value minted minus value burned and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:944` -> `socialize-debt`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `amount`, including far above the real debt (the capping path)
- Exploit idea: `socialize-debt` writes down `lindex` by one ratio while reducing `assets` by a completely different `principal-reduction`. Reach it through `repay` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `repay` with `amount`, including far above the real debt (the capping path), then read `socialize-debt` state before and after in the same block and assert the two sides of the invariant are equal.
