# Q5923: refresh via repay: mint shares whose backing was never received

## Question
`refresh` (mainnet/contracts/market/v0-market-vault.clar:171) rewrites `mask` and stamps `last-update` to `stacks-block-time` on every write. Can an unprivileged caller of `repay` (mainnet/contracts/market/v0-4-market.clar:1316), by choosing `amount`, including far above the real debt (the capping path), use that to mint shares whose backing was never received, violating the invariant that value leaving a call equals value entering plus value minted minus value burned and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/market/v0-market-vault.clar:171` -> `refresh`
- Entrypoint: `repay` (`mainnet/contracts/market/v0-4-market.clar:1316`), unprivileged and publicly callable
- Attacker controls: `amount`, including far above the real debt (the capping path)
- Exploit idea: `refresh` rewrites `mask` and stamps `last-update` to `stacks-block-time` on every write. Reach it through `repay` and mint shares whose backing was never received.
- Invariant to test: value leaving a call equals value entering plus value minted minus value burned
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `repay` with `amount`, including far above the real debt (the capping path), then read `refresh` state before and after in the same block and assert the two sides of the invariant are equal.
