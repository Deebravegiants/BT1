# Q5131: unpack-u16 via borrow: make the per-user ledger and the vault aggregate disagree 

## Question
`unpack-u16` (mainnet/contracts/vault/v0-vault-stx.clar:259) unpacks eight u16 curve fields from one packed word. Can an unprivileged caller of `borrow` (mainnet/contracts/market/v0-4-market.clar:1238), by choosing the order of accrual versus price resolution inside the let, use that to make the per-user ledger and the vault aggregate disagree by a repeatable amount, violating the invariant that `assets` never exceeds the underlying the vault actually holds and producing direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:259` -> `unpack-u16`
- Entrypoint: `borrow` (`mainnet/contracts/market/v0-4-market.clar:1238`), unprivileged and publicly callable
- Attacker controls: the order of accrual versus price resolution inside the let
- Exploit idea: `unpack-u16` unpacks eight u16 curve fields from one packed word. Reach it through `borrow` and make the per-user ledger and the vault aggregate disagree by a repeatable amount.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `borrow` with the order of accrual versus price resolution inside the let, then read `unpack-u16` state before and after in the same block and assert the two sides of the invariant are equal.
