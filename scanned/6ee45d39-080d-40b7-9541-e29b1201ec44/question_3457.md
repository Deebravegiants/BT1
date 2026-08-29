# Q3457: interpolate-rate via deposit: record a repayment larger than the value actually delivere

## Question
Can an unprivileged attacker entering through `deposit` (mainnet/contracts/vault/v0-vault-stx.clar:763), controlling whether the vault is at a zero-supply or zero-asset edge, drive `interpolate-rate` (mainnet/contracts/vault/v0-vault-stx.clar:196) — which interpolates between packed u16 curve points — to record a repayment larger than the value actually delivered, breaking the invariant that `assets` never exceeds the underlying the vault actually holds, and cause direct theft of user funds at rest or in motion?

## Target
- File/function: `mainnet/contracts/vault/v0-vault-stx.clar:196` -> `interpolate-rate`
- Entrypoint: `deposit` (`mainnet/contracts/vault/v0-vault-stx.clar:763`), unprivileged and publicly callable
- Attacker controls: whether the vault is at a zero-supply or zero-asset edge
- Exploit idea: `interpolate-rate` interpolates between packed u16 curve points. Reach it through `deposit` and record a repayment larger than the value actually delivered.
- Invariant to test: `assets` never exceeds the underlying the vault actually holds
- Expected Immunefi impact: Critical - direct theft of user funds at rest or in motion
- Fast validation: In `local-testing/tests` on a local fork, drive `deposit` with whether the vault is at a zero-supply or zero-asset edge, then read `interpolate-rate` state before and after in the same block and assert the two sides of the invariant are equal.
