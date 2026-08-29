# Q2323: total-assets via transfer: destroy value through a truncation the opposite operation 

## Question
`total-assets` (mainnet/contracts/vault/v0-vault-stx.clar:334) adds `(- debt borrowed)` as accrued interest that no token in the vault yet backs. Can an unprivileged caller of `transfer` (mainnet/contracts/vault/v0-vault-stx.clar:752), by choosing the timing relative to a pledge or a liquidation, use that to destroy value through a truncation the opposite operation does not restore, violating the invariant that the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt` and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:334` -> `total-assets`
- Entrypoint: `transfer` (`mainnet/contracts/vault/v0-vault-stx.clar:752`), unprivileged and publicly callable
- Attacker controls: the timing relative to a pledge or a liquidation
- Exploit idea: `total-assets` adds `(- debt borrowed)` as accrued interest that no token in the vault yet backs. Reach it through `transfer` and destroy value through a truncation the opposite operation does not restore.
- Invariant to test: the sum over users of the market-vault `debt` map times `index` equals the vault's `total-debt`
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `transfer` with the timing relative to a pledge or a liquidation, then read `total-assets` state before and after in the same block and assert the two sides of the invariant are equal.
