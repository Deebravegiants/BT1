# Q3115: unpack-u16 via deposit: count one deposit as backing for two simultaneous claims

## Question
`unpack-u16` (mainnet/contracts/vault/v0-vault-stx.clar:259) unpacks eight u16 curve fields from one packed word. Can an unprivileged caller of `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763), by choosing `recipient`, including a contract principal, use that to count one deposit as backing for two simultaneous claims, violating the invariant that tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:259` -> `unpack-u16`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: `recipient`, including a contract principal
- Exploit idea: `unpack-u16` unpacks eight u16 curve fields from one packed word. Reach it through `deposit` and count one deposit as backing for two simultaneous claims.
- Invariant to test: tokens held by .v0-market-vault equal the sum of its `collateral` map for that asset
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `deposit` with `recipient`, including a contract principal, then read `unpack-u16` state before and after in the same block and assert the two sides of the invariant are equal.
